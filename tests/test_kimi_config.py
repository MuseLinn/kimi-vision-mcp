"""Tests for kimi-code config.toml auto-discovery."""

import textwrap
from pathlib import Path

from src.kimi_config import (
    discover_vision_models,
    load_kimi_vision_config,
    select_best_vision_model,
)


def _write_config(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "config.toml"
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


# ── discover_vision_models ──────────────────────────────────────────


def test_discover_vision_models_basic(tmp_path):
    config = _write_config(
        tmp_path,
        """
        [providers.opencode-go]
        type = "openai"
        api_key = "sk-test-123"
        base_url = "https://opencode.ai/zen/go/v1"

        [models."opencode-go/mimo-v2.5"]
        provider = "opencode-go"
        model = "mimo-v2.5"
        capabilities = ["image_in", "video_in", "thinking", "tool_use"]
        display_name = "MiMo V2.5"

        [models."opencode-go/deepseek-v4-flash"]
        provider = "opencode-go"
        model = "deepseek-v4-flash"
        capabilities = ["thinking", "tool_use"]
        display_name = "DeepSeek V4 Flash"
        """,
    )
    candidates = discover_vision_models(config)
    assert len(candidates) == 1
    assert candidates[0].model == "mimo-v2.5"
    assert candidates[0].api_key == "sk-test-123"
    assert candidates[0].has_image is True
    assert candidates[0].has_video is True
    assert candidates[0].display_name == "MiMo V2.5"


def test_discover_vision_models_multiple(tmp_path):
    config = _write_config(
        tmp_path,
        """
        [providers.opencode-go]
        type = "openai"
        api_key = "sk-abc"
        base_url = "https://opencode.ai/zen/go/v1"

        [providers.opencode]
        type = "openai"
        api_key = "sk-xyz"
        base_url = "https://opencode.ai/zen/v1"

        [models."opencode-go/mimo-v2.5"]
        provider = "opencode-go"
        model = "mimo-v2.5"
        capabilities = ["image_in", "video_in", "thinking"]
        display_name = "MiMo V2.5"

        [models."opencode/qwen3.5-plus"]
        provider = "opencode"
        model = "qwen3.5-plus"
        capabilities = ["image_in", "video_in", "thinking"]
        display_name = "Qwen3.5 Plus"

        [models."opencode/glm-5"]
        provider = "opencode"
        model = "glm-5"
        capabilities = ["thinking"]
        display_name = "GLM-5"
        """,
    )
    candidates = discover_vision_models(config)
    assert len(candidates) == 2
    names = {c.display_name for c in candidates}
    assert "MiMo V2.5" in names
    assert "Qwen3.5 Plus" in names
    assert "GLM-5" not in names


def test_discover_skips_missing_provider(tmp_path):
    config = _write_config(
        tmp_path,
        """
        [models."ghost/ghost-model"]
        provider = "nonexistent"
        model = "ghost-model"
        capabilities = ["image_in"]
        display_name = "Ghost Model"
        """,
    )
    candidates = discover_vision_models(config)
    assert len(candidates) == 0


def test_discover_missing_config(tmp_path):
    candidates = discover_vision_models(tmp_path / "nonexistent.toml")
    assert candidates == []


# ── select_best_vision_model ────────────────────────────────────────


def test_select_best_preferred_match(tmp_path):
    config = _write_config(
        tmp_path,
        """
        [providers.p1]
        type = "openai"
        api_key = "sk-1"
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
        """,
    )
    candidates = discover_vision_models(config)
    selected = select_best_vision_model(candidates, preferred="p1/model-b")
    assert selected is not None
    assert selected.model == "model-b"


def test_select_best_fallback_first(tmp_path):
    config = _write_config(
        tmp_path,
        """
        [providers.p1]
        type = "openai"
        api_key = "sk-1"
        base_url = "https://example.com/v1"

        [models."p1/model-a"]
        provider = "p1"
        model = "model-a"
        capabilities = ["image_in"]
        display_name = "Model A"
        """,
    )
    candidates = discover_vision_models(config)
    selected = select_best_vision_model(candidates, preferred="nonexistent")
    assert selected is not None
    assert selected.model == "model-a"


def test_select_best_empty(tmp_path):
    assert select_best_vision_model([]) is None


# ── load_kimi_vision_config ─────────────────────────────────────────


def test_kimi_vision_config_present(tmp_path):
    config = _write_config(
        tmp_path,
        """
        [kimi-vision]
        default_model = "opencode-go/mimo-v2.5"
        timeout = 600
        max_image_size_mb = 30
        max_video_size_mb = 200
        """,
    )
    kv = load_kimi_vision_config(config)
    assert kv is not None
    assert kv.default_model == "opencode-go/mimo-v2.5"
    assert kv.timeout == 600
    assert kv.max_image_size_mb == 30
    assert kv.max_video_size_mb == 200


def test_kimi_vision_config_missing(tmp_path):
    config = _write_config(
        tmp_path,
        """
        [providers.p1]
        type = "openai"
        api_key = "sk-1"
        base_url = "https://example.com/v1"
        """,
    )
    kv = load_kimi_vision_config(config)
    assert kv is None


def test_kimi_vision_config_partial(tmp_path):
    config = _write_config(
        tmp_path,
        """
        [kimi-vision]
        default_model = "opencode-go/qwen3.5-plus"
        """,
    )
    kv = load_kimi_vision_config(config)
    assert kv is not None
    assert kv.default_model == "opencode-go/qwen3.5-plus"
    assert kv.timeout == 300  # default
    assert kv.max_image_size_mb == 20  # default
