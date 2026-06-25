"""Tests for settings configuration."""

import textwrap

import pytest

from src.config import load_settings, list_vision_models


def test_settings_from_explicit_env(monkeypatch):
    monkeypatch.setenv("VISION_API_KEY", "sk-explicit")
    monkeypatch.setenv("VISION_BASE_URL", "https://custom.api/v1")
    monkeypatch.setenv("VISION_MODEL", "custom-model")
    monkeypatch.delenv("MOONSHOT_API_KEY", raising=False)
    monkeypatch.delenv("VISION_TIMEOUT", raising=False)

    settings = load_settings()
    assert settings.api_key == "sk-explicit"
    assert settings.base_url == "https://custom.api/v1"
    assert settings.model == "custom-model"
    assert settings.source == "env"


def test_settings_moonshot_fallback(monkeypatch):
    monkeypatch.delenv("VISION_API_KEY", raising=False)
    monkeypatch.delenv("VISION_BASE_URL", raising=False)
    monkeypatch.delenv("VISION_MODEL", raising=False)
    monkeypatch.setenv("MOONSHOT_API_KEY", "sk-moonshot")
    monkeypatch.delenv("VISION_TIMEOUT", raising=False)

    settings = load_settings()
    assert settings.api_key == "sk-moonshot"
    assert settings.base_url == "https://api.moonshot.ai/v1"
    assert settings.model == "kimi-k2.7-code"
    assert settings.source == "moonshot"


def test_settings_timeout_validation(monkeypatch):
    monkeypatch.delenv("VISION_API_KEY", raising=False)
    monkeypatch.delenv("VISION_BASE_URL", raising=False)
    monkeypatch.delenv("VISION_MODEL", raising=False)
    monkeypatch.setenv("MOONSHOT_API_KEY", "sk-test")
    monkeypatch.setenv("VISION_TIMEOUT", "5")

    with pytest.raises(ValueError, match="VISION_TIMEOUT"):
        load_settings()


def test_settings_missing_key_raises(monkeypatch):
    monkeypatch.delenv("VISION_API_KEY", raising=False)
    monkeypatch.delenv("VISION_BASE_URL", raising=False)
    monkeypatch.delenv("VISION_MODEL", raising=False)
    monkeypatch.delenv("MOONSHOT_API_KEY", raising=False)

    with pytest.raises(ValueError, match="No vision model configured"):
        load_settings()


def test_settings_no_require_key(monkeypatch):
    monkeypatch.delenv("VISION_API_KEY", raising=False)
    monkeypatch.delenv("VISION_BASE_URL", raising=False)
    monkeypatch.delenv("VISION_MODEL", raising=False)
    monkeypatch.delenv("MOONSHOT_API_KEY", raising=False)

    settings = load_settings(require_key=False)
    assert settings.api_key == ""
    assert settings.source == "none"


def test_list_vision_models_from_config(tmp_path, monkeypatch):
    config = tmp_path / "config.toml"
    config.write_text(
        "[providers.opencode-go]\n"
        'type = "openai"\n'
        'api_key = "sk-test"\n'
        'base_url = "https://opencode.ai/zen/go/v1"\n\n'
        '[models."opencode-go/mimo-v2.5"]\n'
        'provider = "opencode-go"\n'
        'model = "mimo-v2.5"\n'
        'capabilities = ["image_in", "video_in", "thinking"]\n'
        'display_name = "MiMo V2.5"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr("src.kimi_config._kimi_code_config_path", lambda: config)
    monkeypatch.delenv("VISION_MODEL", raising=False)

    result = list_vision_models()
    assert len(result.candidates) == 1
    assert result.selected.model == "mimo-v2.5"


def test_kimi_vision_default_model_overrides_order(tmp_path, monkeypatch):
    """~/.kimi-vision/config.toml default_model selects the right model."""
    config = tmp_path / "config.toml"
    config.write_text(
        textwrap.dedent(
            """\
            default_model = "p1/model-b"
            """
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("src.kimi_config._mcp_config_path", lambda: config)
    monkeypatch.delenv("VISION_MODEL", raising=False)

    # We need a kimi-code config too for model discovery
    monkeypatch.setattr(
        "src.kimi_config._kimi_code_config_path",
        lambda: tmp_path / "kimi.toml",
    )
    (tmp_path / "kimi.toml").write_text(
        textwrap.dedent(
            """\
            [providers.p1]
            type = "openai"
            api_key = "sk-test"
            base_url = "https://example.com/v1"

            [models."p1/model-a"]
            provider = "p1"
            model = "model-a"
            capabilities = ["image_in"]
            display_name = "Model A"

            [models."p1/model-b"]
            provider = "p1"
            model = "model-b"
            capabilities = ["image_in"]
            display_name = "Model B"
            """
        ),
        encoding="utf-8",
    )

    result = list_vision_models()
    assert result.selected.model == "model-b"


def test_env_vision_model_overrides_mcp_default(tmp_path, monkeypatch):
    """VISION_MODEL env var takes priority over ~/.kimi-vision/config.toml default_model."""
    config = tmp_path / "mcp_config.toml"
    config.write_text(
        'default_model = "p1/model-b"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr("src.kimi_config._mcp_config_path", lambda: config)
    monkeypatch.setenv("VISION_MODEL", "p1/model-a")

    monkeypatch.setattr(
        "src.kimi_config._kimi_code_config_path",
        lambda: tmp_path / "kimi.toml",
    )
    (tmp_path / "kimi.toml").write_text(
        textwrap.dedent(
            """\
            [providers.p1]
            type = "openai"
            api_key = "sk-test"
            base_url = "https://example.com/v1"

            [models."p1/model-a"]
            provider = "p1"
            model = "model-a"
            capabilities = ["image_in"]
            display_name = "Model A"

            [models."p1/model-b"]
            provider = "p1"
            model = "model-b"
            capabilities = ["image_in"]
            display_name = "Model B"
            """
        ),
        encoding="utf-8",
    )

    result = list_vision_models()
    assert result.selected.model == "model-a"
