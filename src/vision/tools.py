"""High-level vision analysis tools."""

from pydantic import BaseModel, Field

from src.media import encode_image
from src.providers.base import VisionProvider
from src.prompts import SYSTEM_PROMPTS, build_user_prompt, DetailLevel


class UIToArtifactInput(BaseModel):
    path: str = Field(..., description="UI screenshot path or URL")
    target: str = Field(
        default="react",
        description="react | vue | html | prompt | spec | description",
    )
    prompt: str = Field(default="", description="Extra requirements")


class ExtractTextInput(BaseModel):
    path: str = Field(..., description="Screenshot path or URL")
    source_type: str = Field(
        default="general",
        description="code | terminal | doc | general",
    )


class DiagnoseErrorInput(BaseModel):
    path: str = Field(..., description="Error screenshot path or URL")
    context: str = Field(
        default="",
        description="Error context (language, framework, steps)",
    )


class UnderstandDiagramInput(BaseModel):
    path: str = Field(..., description="Diagram path or URL")
    diagram_type: str = Field(
        default="auto",
        description="auto | architecture | flow | uml | er | system",
    )


class AnalyzeDataVizInput(BaseModel):
    path: str = Field(..., description="Chart/dashboard image path or URL")
    question: str = Field(default="", description="Specific question to answer")


class UIDiffInput(BaseModel):
    before_path: str = Field(..., description="Before screenshot path or URL")
    after_path: str = Field(..., description="After screenshot path or URL")
    focus: str = Field(default="", description="Specific aspects to focus on")


class AnalyzeImageInput(BaseModel):
    path: str = Field(..., description="Local image path or http(s) URL")
    prompt: str = Field(default="", description="Custom analysis prompt")
    detail: str = Field(default="smart", description="brief | smart | detailed")


async def _run_image_analysis(
    provider: VisionProvider,
    task_key: str,
    path: str,
    detail: str,
    extra: str = "",
) -> str:
    image_b64, mime = encode_image(path)
    system = SYSTEM_PROMPTS[task_key]
    user = build_user_prompt(task_key.replace("_", " "), DetailLevel(detail), extra)
    return await provider.analyze_image(image_b64, mime, system, user)


async def ui_to_artifact(provider: VisionProvider, params: UIToArtifactInput) -> str:
    extra = f"Target: {params.target}. {params.prompt}"
    return await _run_image_analysis(provider, "ui_to_artifact", params.path, "smart", extra)


async def extract_text_from_screenshot(
    provider: VisionProvider, params: ExtractTextInput
) -> str:
    extra = f"Source type: {params.source_type}"
    return await _run_image_analysis(
        provider, "extract_text_from_screenshot", params.path, "detailed", extra
    )


async def diagnose_error_screenshot(
    provider: VisionProvider, params: DiagnoseErrorInput
) -> str:
    return await _run_image_analysis(
        provider, "diagnose_error_screenshot", params.path, "detailed", params.context
    )


async def understand_technical_diagram(
    provider: VisionProvider, params: UnderstandDiagramInput
) -> str:
    extra = f"Diagram type: {params.diagram_type}"
    return await _run_image_analysis(
        provider, "understand_technical_diagram", params.path, "smart", extra
    )


async def analyze_data_visualization(
    provider: VisionProvider, params: AnalyzeDataVizInput
) -> str:
    extra = params.question
    return await _run_image_analysis(
        provider, "analyze_data_visualization", params.path, "smart", extra
    )


async def ui_diff_check(provider: VisionProvider, params: UIDiffInput) -> str:
    before_b64, before_mime = encode_image(params.before_path)
    after_b64, after_mime = encode_image(params.after_path)
    system = SYSTEM_PROMPTS["ui_diff_check"]
    user = build_user_prompt("ui diff check", DetailLevel.SMART, params.focus)

    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"Before image:\n{user}"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{before_mime};base64,{before_b64}"},
                },
                {"type": "text", "text": "After image:"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{after_mime};base64,{after_b64}"},
                },
            ],
        },
    ]
    return await provider.chat(messages)


async def analyze_image(provider: VisionProvider, params: AnalyzeImageInput) -> str:
    return await _run_image_analysis(
        provider, "analyze_image", params.path, params.detail, params.prompt
    )
