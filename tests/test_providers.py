import httpx
import pytest
import respx

from src.providers.moonshot import MoonshotProvider


@pytest.fixture
def provider():
    return MoonshotProvider(
        api_key="sk-test",
        base_url="https://api.moonshot.ai/v1",
        model="kimi-k2.7-code",
    )


@respx.mock
async def test_analyze_image(provider):
    route = respx.post("https://api.moonshot.ai/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={"choices": [{"message": {"content": "A red circle on white background."}}]},
        )
    )
    result = await provider.analyze_image("b64", "image/png", "You are helpful.", "Describe")
    assert result == "A red circle on white background."
    assert route.called


@respx.mock
async def test_chat(provider):
    respx.post("https://api.moonshot.ai/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Hello"}}]},
        )
    )
    result = await provider.chat([{"role": "user", "content": "Hi"}])
    assert result == "Hello"


@respx.mock
async def test_analyze_image_error(provider):
    respx.post("https://api.moonshot.ai/v1/chat/completions").mock(
        return_value=httpx.Response(401, json={"error": {"message": "Invalid API key"}})
    )
    with pytest.raises(httpx.HTTPStatusError):
        await provider.analyze_image("b64", "image/png", "You are helpful.", "Describe")
