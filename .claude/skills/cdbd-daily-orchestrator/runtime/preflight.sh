#!/bin/zsh
# 저비용 자가진단. 0=통과, 1=실패. 라이브 로그인/ MCP 체크는 매니저가 함.
set -u
VAULT="/Users/designer/Documents/GitHub/design/cdbd-templates"
fail() { echo "PREFLIGHT FAIL: $1"; exit 1; }

[ -f "$HOME/.config/cdbd/credentials.json" ] || fail "OpenAI creds 없음"
[ -f "$VAULT/.env" ] || fail ".env 없음"
grep -q "CDBD_EMAIL" "$VAULT/.env" || fail ".env에 CDBD_EMAIL 없음"
grep -q "CDBD_PASSWORD" "$VAULT/.env" || fail ".env에 CDBD_PASSWORD 없음"
/usr/bin/curl -sf -o /dev/null --max-time 15 "https://www.cdbd.in/login" || fail "cdbd.in 도달 불가(네트워크)"

echo "PREFLIGHT OK"
exit 0
