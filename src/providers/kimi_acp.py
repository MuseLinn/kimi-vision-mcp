"""Vision provider backed by Kimi Code CLI ACP server."""

import asyncio
import json
import os
import random
import subprocess


class KimiACPProvider:
    """Vision provider communicating with Kimi Code CLI via ACP JSON-RPC.

    Starts ``kimi acp`` as a subprocess and drives the Agent Client Protocol:
    initialize → authenticate → session/new → session/prompt (with image blocks).

    Requires a working, authenticated ``kimi`` CLI on $PATH
    (no API key needed — uses Kimi Code's OAuth session).
    """

    def __init__(self, kimi_binary: str = "kimi", timeout: int = 120):
        self._kimi_binary = kimi_binary
        self._timeout = timeout
        self._proc: subprocess.Popen | None = None
        self._session_id: str | None = None
        self._lock = asyncio.Lock()
        self._running = False

        # Async IO — filled by _start()
        self._stdin: asyncio.StreamWriter | None = None
        self._reader_task: asyncio.Task | None = None
        self._msg_queue: asyncio.Queue = asyncio.Queue()

    # ------------------------------------------------------------------
    # Public API  (matches VisionProvider interface)
    # ------------------------------------------------------------------

    async def start(self):
        """Launch ``kimi acp`` and establish an ACP session."""
        self._proc = await asyncio.create_subprocess_exec(
            self._kimi_binary,
            "acp",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        self._stdin = self._proc.stdin
        self._running = True

        # Background reader — enqueues every JSON line
        self._reader_task = asyncio.create_task(self._read_stdout())

        await self._initialize()
        await self._authenticate()
        self._session_id = await self._create_session()

    async def stop(self):
        """Terminate the ACP subprocess."""
        self._running = False
        if self._reader_task:
            self._reader_task.cancel()
        if self._proc:
            try:
                self._proc.terminate()
                await asyncio.wait_for(self._proc.wait(), timeout=5)
            except BaseException:
                self._proc.kill()
                await self._proc.wait()

    async def analyze_image(
        self,
        image_b64: str,
        mime: str,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Send an image + text prompt via ACP and return the text reply."""
        full_prompt = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt
        content = [
            {"type": "text", "text": full_prompt},
            {"type": "image", "data": image_b64, "mimeType": mime},
        ]
        return await self._acp_prompt(content)

    async def analyze_video(
        self,
        video_path: str,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Send video frames (via frames) for analysis."""
        # ACP doesn't support video blocks directly — extract frames
        import base64
        import mimetypes

        raw = open(video_path, "rb").read()
        video_b64 = base64.b64encode(raw).decode("utf-8")
        mime, _ = mimetypes.guess_type(video_path)
        mime = mime or "video/mp4"

        full_prompt = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt
        content = [
            {"type": "text", "text": full_prompt},
            {"type": "image", "data": video_b64, "mimeType": mime},
        ]
        return await self._acp_prompt(content)

    async def chat(self, messages: list[dict]) -> str:
        """Send a conversational prompt (text only)."""
        text = messages[-1]["content"] if isinstance(messages[-1].get("content"), str) else str(messages[-1].get("content", ""))
        return await self._acp_prompt([{"type": "text", "text": text}])

    # ------------------------------------------------------------------
    # ACP protocol helpers
    # ------------------------------------------------------------------

    async def _send(self, method: str, params: dict) -> int:
        """Write a JSON-RPC request to the ACP subprocess."""
        req_id = random.randint(10000, 99999)
        body = json.dumps({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params})
        self._stdin.write((body + "\n").encode())
        await self._stdin.drain()
        return req_id

    async def _wait_response(self, req_id: int, timeout: int = 120) -> dict:
        """Wait for a JSON-RPC response matching *req_id*."""
        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            try:
                msg = await asyncio.wait_for(self._msg_queue.get(), timeout=5)
            except asyncio.TimeoutError:
                continue
            if msg.get("id") == req_id:
                if "error" in msg:
                    raise RuntimeError(
                        f"ACP {msg.get('error', {}).get('message', 'unknown error')}"
                    )
                return msg.get("result", {})
        raise TimeoutError(f"No ACP response for id={req_id} after {timeout}s")

    def _find_response(self, req_id: int) -> dict | None:
        """Synchronously peek the in-memory queue for a matching response."""
        for msg in list(self._msg_queue._queue):
            if msg.get("id") == req_id:
                return msg.get("result")
        return None

    async def _initialize(self):
        req = await self._send("initialize", {"protocolVersion": 1})
        await self._wait_response(req)

    async def _authenticate(self):
        req = await self._send("authenticate", {"methodId": "login"})
        await self._wait_response(req)

    async def _create_session(self) -> str:
        req = await self._send("session/new", {
            "cwd": os.getcwd(),
            "mcpServers": [],
        })
        result = await self._wait_response(req, timeout=30)
        sid = result.get("sessionId")
        if not sid:
            raise RuntimeError("ACP session/new returned no sessionId")
        return sid

    async def _acp_prompt(self, content: list[dict]) -> str:
        """Send a prompt and collect the agent's text reply.

        ACP streams ``agent_message_chunk`` notifications, then sends the
        ``session/prompt`` response (``stopReason``).  We collect chunks
        until we see that response.
        """
        async with self._lock:
            req = await self._send("session/prompt", {
                "sessionId": self._session_id,
                "prompt": content,
            })
            chunks: list[str] = []
            deadline = asyncio.get_event_loop().time() + self._timeout

            while asyncio.get_event_loop().time() < deadline:
                try:
                    msg = await asyncio.wait_for(self._msg_queue.get(), timeout=2)
                except asyncio.TimeoutError:
                    continue

                # session/prompt result → all chunks already consumed
                if msg.get("id") == req:
                    return "".join(chunks)

                # Streaming agent message
                if msg.get("method") == "session/update":
                    upd = msg.get("params", {}).get("update", {})
                    if isinstance(upd, dict) and upd.get("sessionUpdate") == "agent_message_chunk":
                        c = upd.get("content", {})
                        if isinstance(c, dict) and c.get("type") == "text":
                            chunks.append(c["text"])

            return "".join(chunks)

    async def _read_stdout(self):
        """Background reader: parse JSON lines and enqueue."""
        try:
            while self._running and self._proc and self._proc.stdout:
                line = await self._proc.stdout.readline()
                if not line:
                    break
                line = line.decode().strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    await self._msg_queue.put(msg)
                except json.JSONDecodeError:
                    pass
        except (BrokenPipeError, ConnectionResetError):
            pass
        except asyncio.CancelledError:
            pass
