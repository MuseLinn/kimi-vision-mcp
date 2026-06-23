# Tool Reference

All tools are prefixed with `vision_` and are read-only (`readOnlyHint: true`).

## `vision_analyze_image`

General-purpose image understanding.

**Input:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | yes | Local path or http(s) URL |
| `prompt` | string | no | Custom question/instruction |
| `detail` | string | no | `brief`, `smart` (default), or `detailed` |

**Example:**

```
vision_analyze_image(path="/Users/me/photo.png", prompt="What color is the car?")
```

## `vision_ui_to_artifact`

Convert a UI screenshot into code, a prompt, a spec, or a description.

**Input:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | yes | Screenshot path or URL |
| `target` | string | no | `react`, `vue`, `html`, `prompt`, `spec`, `description` |
| `prompt` | string | no | Extra requirements |

## `vision_extract_text`

OCR for screenshots. Optimized for code, terminal output, documents, or general images.

**Input:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | yes | Screenshot path or URL |
| `source_type` | string | no | `code`, `terminal`, `doc`, `general` |

## `vision_diagnose_error`

Analyze an error screenshot and propose fixes.

**Input:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | yes | Error screenshot path or URL |
| `context` | string | no | Language, framework, or reproduction steps |

## `vision_understand_diagram`

Interpret technical diagrams.

**Input:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | yes | Diagram path or URL |
| `diagram_type` | string | no | `auto`, `architecture`, `flow`, `uml`, `er`, `system` |

## `vision_analyze_data_viz`

Extract insights from charts and dashboards.

**Input:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | yes | Chart image path or URL |
| `question` | string | no | Specific question to answer |

## `vision_ui_diff_check`

Compare two UI screenshots.

**Input:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `before_path` | string | yes | Before screenshot path or URL |
| `after_path` | string | yes | After screenshot path or URL |
| `focus` | string | no | Aspects to focus on |

## `vision_analyze_video`

Analyze a local or remote video and return a structured summary.

**Input:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | yes | Local path or http(s) URL |
| `detail` | string | no | `brief`, `smart` (default), `detailed`, `frames` |
| `focus` | string | no | Focus instruction, e.g., `"analyze 0:15-0:25"` |
| `prompt_override` | string | no | Fully override the default prompt |

**Output fields:** `summary`, `key_moments`, `topics`, `visual_elements`, `file_size_mb`, `estimated_time`, `detail_level`.
