#!/bin/zsh
set -eu
SRC="$(cd "$(dirname "$0")/runtime" && pwd)"
DEST="$HOME/.config/cdbd/automation"
PLIST="$HOME/Library/LaunchAgents/in.cdbd.daily-template.plist"
mkdir -p "$DEST/logs"

for f in run-daily.sh preflight.sh notify.sh; do
  cp "$SRC/$f" "$DEST/$f"; chmod +x "$DEST/$f"
done
[ -f "$DEST/state.json" ] || cp "$SRC/state.seed.json" "$DEST/state.json"
cp "$SRC/in.cdbd.daily-template.plist" "$PLIST"

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "installed. 현재 등록 상태:"
launchctl list | grep cdbd || echo "(grep cdbd: 없음 — 확인 필요)"
