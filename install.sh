#!/usr/bin/env bash
# Install the research-to-paper skills into Claude Code and/or Codex (macOS / Linux).
# Usage: bash install.sh [all|claude|codex]
#   claude -> ~/.claude/skills/    codex -> ~/.codex/skills/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILLS="$ROOT/skills"
TARGET="${1:-all}"
[ -d "$SKILLS" ] || { echo "skills/ not found at $SKILLS" >&2; exit 1; }

copy_skills() {                       # $1 = destination skills dir
  local dst="$1"; mkdir -p "$dst"
  for s in "$SKILLS"/*/; do
    local name; name="$(basename "$s")"
    rm -rf "$dst/$name"
    cp -r "$s" "$dst/$name"
  done
}

install_claude() { copy_skills "$HOME/.claude/skills"; echo "✓ Claude Code skills → $HOME/.claude/skills/"; }
install_codex()  { copy_skills "$HOME/.codex/skills";  echo "✓ Codex skills → $HOME/.codex/skills/"; }

case "$TARGET" in
  all)    install_claude; install_codex ;;
  claude) install_claude ;;
  codex)  install_codex ;;
  *) echo "Usage: bash install.sh [all|claude|codex]" >&2; exit 1 ;;
esac
echo "Done. Restart Claude Code / Codex, then ask it to use research-to-paper."
