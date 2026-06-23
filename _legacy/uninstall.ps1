# Video Analyzer MCP Server — PowerShell 卸载脚本
# 用法: irm https://raw.githubusercontent.com/MuseLinn/video-analyzer-mcp/master/uninstall.ps1 | iex

$ErrorActionPreference = "Stop"

$InstallDir = Join-Path $env:USERPROFILE ".mcp" "video-analyzer"

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }

if (-not (Test-Path $InstallDir)) {
    Write-Info "未找到安装目录 $InstallDir，无需卸载"
    exit 0
}

Write-Info "正在卸载 Video Analyzer MCP Server..."
Remove-Item -Recurse -Force $InstallDir
Write-Success "已删除 $InstallDir"

Write-Host ""
Write-Warn "请手动从 Agent 配置中删除 video-analyzer 相关配置："
Write-Host "  - %USERPROFILE%\.opencode\opencode.jsonc"
Write-Host "  - %USERPROFILE%\.hermes\config.yaml"
Write-Host "  - Claude Desktop / Cursor 配置"
