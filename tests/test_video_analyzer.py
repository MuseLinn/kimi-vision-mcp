import httpx
import respx

from src.providers.moonshot import MoonshotProvider
from src.video.analyzer import AnalyzeVideoInput, analyze_video_file


@respx.mock
async def test_analyze_video_file(tmp_path):
    video = tmp_path / "test.mp4"
    video.write_bytes(b"fake video data" + b"x" * 1024 * 1024)

    respx.post("https://api.moonshot.ai/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"content": '{"summary": "A demo video", "key_moments": []}'}}
                ]
            },
        )
    )

    provider = MoonshotProvider("sk-test", "https://api.moonshot.ai/v1", "kimi-k2.7-code")
    result = await analyze_video_file(provider, AnalyzeVideoInput(path=str(video), detail="brief"))
    assert result["summary"] == "A demo video"
    assert result["detail_level"] == "brief"
    assert result["file_size_mb"] > 0
