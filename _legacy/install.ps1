# Video Analyzer MCP Server — PowerShell 安装脚本
# 用法: irm https://raw.githubusercontent.com/MuseLinn/video-analyzer-mcp/master/install.ps1 | iex

$ErrorActionPreference = "Stop"

$InstallDir = Join-Path $env:USERPROFILE ".mcp" "video-analyzer"
$RepoUrl = "https://github.com/MuseLinn/video-analyzer-mcp.git"

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-OK($msg) { Write-Host "[OK]   $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "[ERR]  $msg" -ForegroundColor Red }

function Test-Command($cmd) {
    $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

Write-Info "Video Analyzer MCP Server — 安装"
Write-Host "========================================" -ForegroundColor Cyan

Write-Info "检测 Python..."
if (-not (Test-Command "python")) {
    Write-Err "未找到 python 命令。请先安装 Python 3: https://python.org"
    exit 1
}
$python = (Get-Command python).Source
Write-OK "Python: $python"

Write-Info "检测 mcp 包..."
& $python -c "import mcp" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-OK "mcp 已安装"
} else {
    Write-Warn "mcp 未安装，尝试安装..."
    & $python -m pip install mcp
    if ($LASTEXITCODE -eq 0) {
        Write-OK "mcp 安装成功"
    } else {
        Write-Err "mcp 安装失败"
        exit 1
    }
}

Write-Info "检测 git..."
if (-not (Test-Command "git")) {
    Write-Err "未找到 git。请先安装 Git: https://git-scm.com/download/win"
    exit 1
}
Write-OK "git: $(Get-Command git).Source"

Write-Info "检测 kimi-cli..."
if (-not (Test-Command "kimi")) {
    Write-Err "未找到 kimi 命令。请先安装 kimi-cli: https://github.com/MoonshotAI/kimi-cli"
    exit 1
}
Write-OK "kimi-cli: $(Get-Command kimi).Source"

Write-Info "安装代码..."
$gitDir = Join-Path $InstallDir ".git"
if (Test-Path $gitDir) {
    Write-Info "目录已存在，尝试更新..."
    Push-Location $InstallDir
    git pull
    Pop-Location
} elseif (Test-Path $InstallDir) {
    Write-Warn "安装目录存在但不是 git repo，将重新克隆..."
    Remove-Item -Recurse -Force $InstallDir
    git clone $RepoUrl $InstallDir
} else {
    git clone $RepoUrl $InstallDir
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-OK "安装完成!"
Write-Host ""
Write-Host "📁 代码位置: $InstallDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 下一步:" -ForegroundColor Cyan
Write-Host "   1. 参照 README 配置你的 Agent"
Write-Host "   2. 重启 Agent"
Write-Host ""
Write-Host "⚠️  重要: 视频分析耗时较长，请确保 MCP timeout >= 300 秒" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
