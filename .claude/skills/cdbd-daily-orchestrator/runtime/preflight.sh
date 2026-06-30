#!/bin/zsh
# 저비용 자가진단. 0=통과, 1=실패. 라이브 로그인/ MCP 체크는 매니저가 함.
set -u
VAULT="/Users/designer/Documents/GitHub/design/cdbd-templates"
fail() { echo "PREFLIGHT FAIL: $1"; exit 1; }

[ -f "$HOME/.config/cdbd/credentials.json" ] || fail "OpenAI creds 없음"
[ -f "$VAULT/.env" ] || fail ".env 없음 (또는 Documents 접근권한 없음 → /bin/zsh에 전체 디스크 접근 허용 필요)"
# zsh가 직접 파일을 읽음(grep 자식 프로세스 미사용) → FDA가 zsh에만 있어도 동작
ENV_CONTENT="$(<"$VAULT/.env")" || fail ".env 읽기 실패 (전체 디스크 접근 권한 확인)"
[[ "$ENV_CONTENT" == *CDBD_EMAIL* ]]    || fail ".env에 CDBD_EMAIL 없음"
[[ "$ENV_CONTENT" == *CDBD_PASSWORD* ]] || fail ".env에 CDBD_PASSWORD 없음"
/usr/bin/curl -sf -o /dev/null --max-time 15 "https://www.cdbd.in/login" || fail "cdbd.in 도달 불가(네트워크)"

echo "PREFLIGHT OK"
exit 0
