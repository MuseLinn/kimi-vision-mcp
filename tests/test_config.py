import pytest

from src.config import load_settings


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("MOONSHOT_API_KEY", "sk-test")
    monkeypatch.setenv("VISION_MODEL", "kimi-k2-6-code")
    monkeypatch.setenv("VISION_TIMEOUT", "120")

    settings = load_settings()
    assert settings.api_key == "sk-test"
    assert settings.model == "kimi-k2-6-code"
    assert settings.timeout == 120


def test_settings_defaults(monkeypatch):
    monkeypatch.setenv("MOONSHOT_API_KEY", "sk-test")
    monkeypatch.delenv("VISION_MODEL", raising=False)
    monkeypatch.delenv("VISION_TIMEOUT", raising=False)

    settings = load_settings()
    assert settings.base_url == "https://api.moonshot.ai/v1"
    assert settings.model == "kimi-k2-6-code"
    assert settings.timeout == 300


def test_settings_missing_key_raises(monkeypatch):
    monkeypatch.delenv("MOONSHOT_API_KEY", raising=False)
    with pytest.raises(ValueError, match="MOONSHOT_API_KEY"):
        load_settings()


def test_settings_timeout_validation(monkeypatch):
    monkeypatch.setenv("MOONSHOT_API_KEY", "sk-test")
    monkeypatch.setenv("VISION_TIMEOUT", "5")
    with pytest.raises(ValueError, match="VISION_TIMEOUT"):
        load_settings()
