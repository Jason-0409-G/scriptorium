<#
  research-to-paper · Windows 一键安装(可选 DeepSeek 后端)
  ───────────────────────────────────────────────────────────
  它会:① 装 Node.js(如缺)→ ② 用淘宝镜像装 Claude Code → ③ 装 research-to-paper
        7 个 skill → ④ (可选)把后端配成 DeepSeek。装完重开终端输入 claude 即可。

  用法:
    1) 用「记事本」打开本文件,把下面 $DeepSeekApiKey 引号里换成你的 DeepSeek API Key
       (不想用 DeepSeek、走官方 Anthropic 登录的,这一行留空即可)。
    2) 在本文件所在文件夹开 PowerShell,运行:
         powershell -ExecutionPolicy Bypass -File .\setup-windows.ps1
       (若提示文件被阻止,先运行:  Unblock-File .\setup-windows.ps1  )

  ⚠ 安全:填好 key 的脚本是「带凭据」的,**不要提交到 Git / 不要公开**。
    要给别人用,就把填好的副本私下发给对方;对方也可自己注册 DeepSeek key 填入。
#>

# ===================== 只需改这一行 =====================
$DeepSeekApiKey = ""                              # ← 填你的 DeepSeek API Key;留空则走 Anthropic 官方登录
# ===================== 可选项(一般不用动) ==============
$Model      = "deepseek-v4-pro"                    # 主模型;以 DeepSeek 官方接入文档为准(模型名会随版本变)
$HaikuModel = "deepseek-v4-flash"                  # 后台小模型;同上,以官方文档为准
$BaseUrl    = "https://api.deepseek.com/anthropic" # DeepSeek 的 Anthropic 兼容端点,以其官方文档为准
# =======================================================

$ErrorActionPreference = "Stop"
function Info($m){ Write-Host "[安装] $m" -ForegroundColor Cyan }
function Ok($m){ Write-Host "[OK]  $m" -ForegroundColor Green }
function Die($m){ Write-Host "[错误] $m" -ForegroundColor Red; exit 1 }
function Have($c){ return [bool](Get-Command $c -ErrorAction SilentlyContinue) }
function RefreshPath(){
  $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
              [Environment]::GetEnvironmentVariable("Path","User")
}

Info "开始安装 research-to-paper(Windows)"

# 1) Node.js(npm 方式需要;缺则尝试 winget,失败给手动指引)
if (-not (Have node)) {
  Info "未检测到 Node.js,尝试用 winget 安装 LTS ..."
  if (Have winget) {
    try { winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements }
    catch { Info "winget 安装 Node 失败,稍后给手动指引" }
    RefreshPath
  }
}
if (-not (Have node)) {
  Die "Node.js 仍不可用。请手动安装(国内镜像:https://npmmirror.com/mirrors/node/ 选最新 LTS 的 .msi),装完重开终端再运行本脚本。"
}
Ok ("Node.js " + (node -v))

# 2) npm 换淘宝镜像,全局装 Claude Code
Info "设置 npm 淘宝镜像(国内加速)..."
npm config set registry https://registry.npmmirror.com
Info "安装 Claude Code(npm 全局,可能要几分钟)..."
npm install -g @anthropic-ai/claude-code
RefreshPath
if (-not (Have claude)) {
  $p = (npm prefix -g) 2>$null
  if ($p) { $env:Path = "$p;$env:Path" }
}
if (Have claude) { Ok ("Claude Code " + (claude --version)) }
else { Info "Claude Code 已装,但当前终端 PATH 未刷新;装完重开终端即可用 claude。" }

# 3) 下载并安装 research-to-paper 的 7 个 skill(复用仓库自带 install.ps1)
$tmp = Join-Path $env:TEMP ("r2p_" + [Guid]::NewGuid().ToString("N").Substring(0,8))
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$zip = Join-Path $tmp "repo.zip"
$zipUrl = "https://github.com/Jason-0409-G/research-to-paper/archive/refs/heads/main.zip"
Info "下载 research-to-paper ..."
try { Invoke-WebRequest -Uri $zipUrl -OutFile $zip -UseBasicParsing }
catch { Die "下载仓库失败(网络/GitHub 访问问题)。可挂代理后重试,或手动:git clone https://github.com/Jason-0409-G/research-to-paper 然后运行其中的 install.ps1 -Target claude" }
Expand-Archive -Path $zip -DestinationPath $tmp -Force
$installer = Join-Path $tmp "research-to-paper-main\install.ps1"
if (-not (Test-Path $installer)) { Die "解压后未找到 install.ps1,仓库结构可能有变。" }
& $installer -Target claude
Ok "7 个 skill 已安装到 $HOME\.claude\skills\"
Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue

# 4) (可选)配置 DeepSeek 后端 —— 写入 ~/.claude/settings.json,免 Claude 登录
if (-not [string]::IsNullOrWhiteSpace($DeepSeekApiKey)) {
  Info "配置 DeepSeek 后端(免 Claude 登录)..."
  $claudeDir = Join-Path $HOME ".claude"
  New-Item -ItemType Directory -Force -Path $claudeDir | Out-Null
  $settingsPath = Join-Path $claudeDir "settings.json"
  $block = [ordered]@{
    hasCompletedOnboarding = $true        # 关键:不设的话首次 claude 仍可能弹登录/引导
    env = [ordered]@{
      ANTHROPIC_BASE_URL            = $BaseUrl
      ANTHROPIC_AUTH_TOKEN          = $DeepSeekApiKey   # DeepSeek 用 AUTH_TOKEN(Bearer),不是 API_KEY
      ANTHROPIC_MODEL               = $Model
      ANTHROPIC_DEFAULT_HAIKU_MODEL = $HaikuModel
    }
  }
  if (Test-Path $settingsPath) {
    Copy-Item $settingsPath "$settingsPath.bak" -Force
    Info "已存在 settings.json(备份为 settings.json.bak)。为不覆盖你的其它设置,请手动把下面这段并进 env 里:"
    ($block | ConvertTo-Json -Depth 10) | Write-Host
  } else {
    ($block | ConvertTo-Json -Depth 10) | Set-Content -Path $settingsPath -Encoding UTF8
    Ok "DeepSeek 已写入 $settingsPath(base=$BaseUrl · model=$Model · 免登录直用)"
  }
} else {
  Info "未填 DeepSeek Key → 跳过后端配置,首次运行 claude 会走 Anthropic 官方登录(需能访问 claude.ai,国内可能要代理)。"
}

Write-Host ""
Ok "全部完成!"
Write-Host "下一步:关掉本终端,重开一个 PowerShell,输入  claude  即可开始。" -ForegroundColor Yellow
Write-Host "进去后直接说,例如:用 research-to-paper 帮我把这批文献核对 DOI 并导成 Zotero 库。" -ForegroundColor Yellow
