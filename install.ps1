$ProjectDir = "$env:USERPROFILE\projects\video-analyzer-mcp"
$McpDir = "$env:USERPROFILE\.mcp\video-analyzer"

Write-Host "🚀 Installing video-analyzer-mcp to $ProjectDir"

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    Write-Host "❌ Python not found. Please install Python 3.10+."
    exit 1
}

if (Test-Path "$ProjectDir\.git") {
    Write-Host "Updating existing repository..."
    Set-Location $ProjectDir
    git pull
} else {
    Write-Host "Cloning repository..."
    New-Item -ItemType Directory -Force -Path (Split-Path $ProjectDir) | Out-Null
    git clone https://github.com/MuseLinn/video-analyzer-mcp.git $ProjectDir
    Set-Location $ProjectDir
}

& $Python.Path -m pip install -r requirements.txt

New-Item -ItemType Directory -Force -Path $McpDir | Out-Null
$ServerPath = Join-Path $ProjectDir "server.py"
$LinkPath = Join-Path $McpDir "server.py"
if (Test-Path $LinkPath) { Remove-Item $LinkPath }
New-Item -ItemType SymbolicLink -Path $LinkPath -Target $ServerPath | Out-Null

Write-Host "✅ Installed. Add this MCP server to your client:"
Write-Host ""
Write-Host "Claude Code / Desktop:"
Write-Host "  claude mcp add -s user video-analyzer --env MOONSHOT_API_KEY=your_key -- python $ProjectDir\server.py"
Write-Host ""
Write-Host "Or add manually to your MCP config:"
Write-Host "  command: python"
Write-Host "  args: [$ProjectDir\server.py]"
Write-Host "  env: { MOONSHOT_API_KEY: your_key }"
