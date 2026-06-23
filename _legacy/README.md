# Video Analyzer MCP Server

让支持 MCP 的 Agent（Opencode / Hermes / Claude Desktop / Cursor 等）通过 Kimi CLI 进行原生视频多模态分析。

## 核心能力

- **时间连续性理解**：模型直接看视频，不是抽帧，能感知动画节奏、过渡效果、时序逻辑
- **局部聚焦分析**：支持指定时间段或关注点，精准定位问题
- **动效/动画理解**：录制网页/程序的交互视频，分析 easing、transition、状态变化
- **动态耗时估算**：根据文件大小自动估算分析时间，不盲目等待

## 前置依赖

Video Analyzer MCP **依赖 kimi-cli**。安装前请确保已安装：

- **kimi-cli**：https://github.com/MoonshotAI/kimi-cli
- **Python 3.8+**
- **Git**

```bash
# 验证依赖
kimi --version   # 确认 kimi-cli 已安装
python3 --version  # 或 python --version
git --version
```

## 安装

### Linux / macOS（Bash）

```bash
curl -fsSL https://raw.githubusercontent.com/MuseLinn/video-analyzer-mcp/master/install.sh | bash
```

### Windows（PowerShell）

```powershell
irm https://raw.githubusercontent.com/MuseLinn/video-analyzer-mcp/master/install.ps1 | iex
```

> 如果执行策略限制，先运行：`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 手动克隆安装

如果你不想用一键脚本，可以手动克隆并安装依赖：

**Linux / macOS:**
```bash
git clone https://github.com/MuseLinn/video-analyzer-mcp.git ~/.mcp/video-analyzer
pip install mcp
```

**Windows:**
```powershell
git clone https://github.com/MuseLinn/video-analyzer-mcp.git $env:USERPROFILE\.mcp\video-analyzer
pip install mcp
```

**安装脚本不修改任何 Agent 配置文件。** 安装完成后请参照下方"配置"章节手动配置。

### 更新

**最简单的方式：重新运行一键安装命令**（会自动检测并更新）：

**Linux / macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/MuseLinn/video-analyzer-mcp/master/install.sh | bash
```

**Windows:**
```powershell
irm https://raw.githubusercontent.com/MuseLinn/video-analyzer-mcp/master/install.ps1 | iex
```

或者手动更新（进入安装目录执行 git pull）：

**Linux / macOS:**
```bash
cd ~/.mcp/video-analyzer && git pull
```

**Windows:**
```powershell
cd $env:USERPROFILE\.mcp\video-analyzer; git pull
```

### 卸载

**一行命令卸载（无需确认）：**

**Linux / macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/MuseLinn/video-analyzer-mcp/master/uninstall.sh | bash
```

**Windows:**
```powershell
irm https://raw.githubusercontent.com/MuseLinn/video-analyzer-mcp/master/uninstall.ps1 | iex
```

或者手动卸载：

**Linux / macOS:**
```bash
cd ~/.mcp/video-analyzer
python install.py uninstall
```

**Windows:**
```powershell
cd $env:USERPROFILE\.mcp\video-analyzer
python install.py uninstall
```

## 配置

**安装完成后必须手动配置 Agent。** 安装脚本不会修改任何配置文件。

> 配置中的 `command` 用系统默认的 `python` 即可（需要有 `mcp` 包）。不需要指向 kimi-cli 的 Python。

### Opencode

**Linux / macOS**（`~/.opencode/opencode.jsonc`）：
```jsonc
{
  "mcp": {
    "video-analyzer": {
      "type": "local",
      "command": ["python", "~/.mcp/video-analyzer/server.py"]
    }
  }
}
```

**Windows**（`%USERPROFILE%\.opencode\opencode.jsonc`）：
```jsonc
{
  "mcp": {
    "video-analyzer": {
      "type": "local",
      "command": ["python", "C:\\Users\\%USERNAME%\\.mcp\\video-analyzer\\server.py"]
    }
  }
}
```

### Hermes

**Linux / macOS**（`~/.hermes/config.yaml`）：
```yaml
mcp_servers:
  video-analyzer:
    command: "python"
    args: ["~/.mcp/video-analyzer/server.py"]
    timeout: 300
```

**Windows**（`%USERPROFILE%\.hermes\config.yaml`）：
```yaml
mcp_servers:
  video-analyzer:
    command: "python"
    args: ["C:\\Users\\%USERNAME%\\.mcp\\video-analyzer\\server.py"]
    timeout: 300
```

### Claude Desktop / Cursor

**Linux / macOS**（`claude_desktop_config.json`）：
```json
{
  "mcpServers": {
    "video-analyzer": {
      "command": "python",
      "args": ["~/.mcp/video-analyzer/server.py"]
    }
  }
}
```

**Windows**（`claude_desktop_config.json`）：
```json
{
  "mcpServers": {
    "video-analyzer": {
      "command": "python",
      "args": ["C:\\Users\\%USERNAME%\\.mcp\\video-analyzer\\server.py"]
    }
  }
}
```

### 配置后重启 Agent

**修改配置后必须重启 Agent 才能生效。**

## 使用示例

### 基础分析

> "分析这个视频 ~/path/to/your/video.mp4"

### 聚焦时间段

> "分析这个视频，重点关注 0:15-0:25 的过渡动画是否流畅"
> "检查这个视频第 30 秒到 40 秒的文字显示是否清晰"

### 动效/动画分析

> "我录制了网页的交互视频，分析一下这个 hover 效果的 easing 曲线"
> "分析这个 loading 动画，看看有没有卡顿或掉帧"

### 在线视频

> "分析这个视频 https://example.com/video.mp4"
> （或先用 `wget` 下载到本地再分析）

### 不同详细程度

> "简要分析这个视频 ~/path/to/your/video.mp4"        # 最快，约 30-60 秒
> "详细分析这个视频 ~/path/to/your/video.mp4"        # 较慢，约 2-5 分钟
> "逐帧分析这个视频 ~/path/to/your/video.mp4"        # 最慢，谨慎使用

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `path` | string | 必填 | 本地路径或 http(s) URL |
| `detail` | string | "smart" | `brief`(最快) / `smart`(推荐) / `detailed` / `frames`(最慢) |
| `focus` | string | "" | 聚焦指令，如 "分析 0:15-0:25 的过渡" |
| `prompt_override` | string | "" | 完全自定义分析指令 |

### Detail 级别与耗时

| 级别 | 速度 | 适用场景 |
|------|------|---------|
| **brief** | 最快 | 快速了解视频内容，约 30-90 秒 |
| **smart** | 中等 | 平衡深度和速度，约 1-3 分钟 |
| **detailed** | 较慢 | 深入分析，约 2-5 分钟 |
| **frames** | 最慢 | 逐场景细节，约 3-8 分钟 |

实际耗时取决于：
- **文件大小**：上传时间占主要部分（~5s/MB）
- **视频时长**：模型分析时间与内容复杂度相关
- **detail 级别**：brief 比 frames 快 2-4 倍

## 返回值示例

```json
{
  "summary": "产品演示视频，重点展示了新功能的 onboarding 流程",
  "file_size_mb": 2.5,
  "estimated_time": "约 1-2 分钟",
  "key_moments": [
    {"time": "0:00-0:05", "label": "开场", "detail": "Logo 淡入，节奏平稳"},
    {"time": "0:05-0:20", "label": "功能演示", "detail": "主界面展示，建议按钮高亮更明显"}
  ],
  "topics": ["产品演示", "UI/UX", "onboarding"],
  "visual_elements": ["深色主题", "蓝色主色调", "0:12处转场偏快"],
  "full_analysis_path": "~/.video_analysis/a3f7b2_demo.json",
  "token_estimate": "~280 tokens"
}
```

完整分析保存在 `~/.video_analysis/` 目录，按需读取。

## ⚠️ 耗时与超时处理

### 动态耗时估算

Server 会根据文件大小自动估算时间，并在返回结果中提供 `estimated_time`：
- < 1MB: 约 30-90 秒
- 1-5MB: 约 1-2 分钟
- 5-20MB: 约 2-4 分钟
- 20-100MB: 约 3-6 分钟

### 避免超时失败的策略

1. **MCP 配置中设置足够超时**（推荐 300 秒）
2. **先用 `brief` 快速预览**，确认视频内容后再决定是否 deep dive
3. **视频过大时先压缩**：
   ```bash
   ffmpeg -i input.mp4 -vcodec libx264 -crf 28 -preset fast -vf "scale=1280:-2" output.mp4
   ```
4. **超时错误处理**：如果发生超时，返回的错误信息会明确提示解决建议

### 为什么不做成异步回调？

MCP stdio 协议目前不支持 server 主动推送结果。Tool call 是同步阻塞的。我们采用务实的策略：
- 分析前告知预计耗时
- 配置足够长的 timeout
- 用 `brief` 模式做快速预览降低风险

## API 安全模型

### 本地个人使用（推荐）

```
你的机器 ──→ MCP server ──→ import kimi_cli.cli
                              └── 读取 ~/.kimi/config.toml
                                  └── 你的 Kimi 账号
```

- ✅ **零硬编码**：代码中没有 API Key
- ✅ **用户隔离**：每个用户用自己的 `~/.kimi/` 配置
- ✅ **无泄露风险**：Key 由 kimi CLI 内部管理，server 只传递视频路径

### 共享服务器部署

如果在团队服务器上部署，可通过环境变量注入：

```yaml
mcp_servers:
  video-analyzer:
    command: "python"
    args: ["server.py"]
    env:
      KIMI_API_KEY: "${KIMI_API_KEY}"
```

## 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| "kimi login required" | 未登录 | 执行 `kimi login` |
| 超时无响应 | 视频太大或网络慢 | 压缩视频、增加 timeout、改用 brief |
| 返回非 JSON | 模型输出格式不稳定 | 重试，或用 `detail="smart"` |
| URL 下载失败 | 网络限制 | 手动下载后传本地路径 |
| 安装脚本检测不到 kimi | 不在 PATH 中 | 手动指定 python 路径运行 server |

## 开发

```bash
cd ~/.mcp/video-analyzer
python -m video_analyzer.server  # 手动启动 MCP server
```
