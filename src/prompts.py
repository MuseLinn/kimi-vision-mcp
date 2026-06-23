"""System prompts and user prompt builders for vision/video tasks."""

from enum import Enum


class DetailLevel(str, Enum):
    BRIEF = "brief"
    SMART = "smart"
    DETAILED = "detailed"
    FRAMES = "frames"


SYSTEM_PROMPTS = {
    "ui_to_artifact": (
        "You are an expert frontend engineer. Convert the provided UI screenshot "
        "into clean, production-ready code or a detailed implementation spec. "
        "Respond with code when the target is a framework, otherwise respond with "
        "a structured description or prompt."
    ),
    "extract_text_from_screenshot": (
        "You are an OCR assistant. Extract all readable text from the screenshot. "
        "Preserve formatting for code and terminal output. Return plain text or markdown."
    ),
    "diagnose_error_screenshot": (
        "You are a debugging assistant. Analyze the error screenshot, identify the likely "
        "root cause, and propose concrete, actionable fixes. Include file names, line numbers, "
        "or settings if visible."
    ),
    "understand_technical_diagram": (
        "You are a system architect. Interpret the technical diagram and explain the "
        "components, relationships, data flow, and any design trade-offs."
    ),
    "analyze_data_visualization": (
        "You are a data analyst. Read the chart/dashboard and summarize key insights, "
        "trends, anomalies, and numbers. Answer the user's specific question if provided."
    ),
    "ui_diff_check": (
        "You are a QA engineer. Compare the two UI screenshots and list all visual "
        "differences, including layout, color, text, spacing, and missing/added elements."
    ),
    "analyze_image": (
        "You are a helpful visual assistant. Describe the image accurately and answer "
        "the user's question about it."
    ),
    "analyze_video_file": (
        "You are a video analysis assistant. Analyze the video and produce a structured "
        "summary with key moments, topics, visual elements, and any user-requested focus."
    ),
}


def build_user_prompt(task: str, detail: DetailLevel, extra: str = "") -> str:
    detail_instruction = {
        DetailLevel.BRIEF: "Keep the response concise and high-level.",
        DetailLevel.SMART: "Provide a balanced, structured response with key details.",
        DetailLevel.DETAILED: "Provide a thorough, detailed response with examples.",
        DetailLevel.FRAMES: "Analyze scene-by-scene with fine-grained detail.",
    }.get(detail, "")

    prompt = f"Task: {task}. {detail_instruction}"
    if extra:
        prompt += f"\n\nAdditional context: {extra}"
    return prompt
