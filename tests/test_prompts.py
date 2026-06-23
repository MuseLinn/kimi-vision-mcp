from src.prompts import build_user_prompt, DetailLevel, SYSTEM_PROMPTS


def test_system_prompts_exist():
    assert "ui_to_artifact" in SYSTEM_PROMPTS
    assert "analyze_image" in SYSTEM_PROMPTS


def test_build_user_prompt():
    p = build_user_prompt("Describe the UI", DetailLevel.SMART, "Focus on accessibility")
    assert "Describe the UI" in p
    assert "balanced" in p
    assert "accessibility" in p


def test_build_user_prompt_without_extra():
    p = build_user_prompt("Summarize", DetailLevel.BRIEF)
    assert "Summarize" in p
    assert "concise" in p
    assert "Additional context" not in p
