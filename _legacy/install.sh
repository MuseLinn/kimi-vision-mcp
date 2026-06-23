#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/MuseLinn/video-analyzer-mcp.git"
INSTALL_DIR="$HOME/.mcp/video-analyzer"

info() { echo -e "\033[36m[INFO]\033[0m $*"; }
ok()   { echo -e "\033[32m[OK]\033[0m   $*"; }
warn() { echo -e "\033[33m[WARN]\033[0m $*"; }
err()  { echo -e "\033[31m[ERR]\033[0m  $*"; }

info "Video Analyzer MCP Server — 安装"
echo "========================================"

info "检测 Python..."
PYTHON=""
for cmd in python python3; do
    if command -v "$cmd" &>/dev/null && "$cmd" -c "import sys" &>/dev/null 2>&1; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    err "未找到可用的 Python 3。请先安装: https://python.org"
    exit 1
fi
ok "Python: $(command -v "$PYTHON")"

info "检测 mcp 包..."
if "$PYTHON" -c "import mcp" &>/dev/null 2>&1; then
    ok "mcp 已安装"
else
    warn "mcp 未安装，尝试安装..."
    if ! "$PYTHON" -m pip install mcp; then
        err "mcp 安装失败"
        echo ""
        echo "可能的原因："
        echo "  1. pip 未安装: $PYTHON -m ensurepip --upgrade"
        echo "  2. 权限问题: 尝试用虚拟环境"
        echo "  3. 网络问题: 检查网络连接"
        echo ""
        echo "或者手动安装: $PYTHON -m pip install mcp"
        exit 1
    fi
    ok "mcp 安装成功"
fi

info "检测 git..."
if ! command -v git &>/dev/null; then
    err "未找到 git。请先安装 Git"
    exit 1
fi
ok "git: $(command -v git)"

info "检测 kimi-cli..."
if ! command -v kimi &>/dev/null; then
    err "未找到 kimi 命令。请先安装 kimi-cli: https://github.com/MoonshotAI/kimi-cli"
    exit 1
fi
ok "kimi-cli: $(command -v kimi)"

info "安装代码..."
if [ -d "$INSTALL_DIR/.git" ]; then
    info "目录已存在，尝试更新..."
    cd "$INSTALL_DIR"
    git pull
elif [ -d "$INSTALL_DIR" ]; then
    warn "安装目录存在但不是 git repo，将重新克隆..."
    rm -rf "$INSTALL_DIR"
    git clone "$REPO_URL" "$INSTALL_DIR"
else
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

echo ""
echo "========================================"
ok "安装完成!"
echo ""
echo "📁 代码位置: $INSTALL_DIR"
echo ""
echo "📋 下一步:"
echo "   1. 参照 README 配置你的 Agent"
echo "   2. 重启 Agent"
echo ""
echo "⚠️  重要: 视频分析耗时较长，请确保 MCP timeout >= 300 秒"
echo "========================================"
