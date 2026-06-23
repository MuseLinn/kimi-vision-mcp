import httpx
import respx

from src.providers.moonshot import MoonshotProvider
from src.vision.tools import AnalyzeImageInput, analyze_image


@respx.mock
async def test_analyze_image_tool(tmp_path):
    img = tmp_path / "test.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\nfake")

    respx.post("https://api.moonshot.ai/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={"choices": [{"message": {"content": "A screenshot of a login page."}}]},
        )
    )

    provider = MoonshotProvider("sk-test", "https://api.moonshot.ai/v1", "kimi-k2.7-code")
    result = await analyze_image(provider, AnalyzeImageInput(path=str(img)))
    assert "login page" in result
