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
# 네트워크: 깨어난 직후 재연결 지연·일시 blip 대비 재시도 (최대 5회, 15초 간격 = 최대 ~75초)
NET_OK=0
for attempt in 1 2 3 4 5; do
  /usr/bin/curl -sf -o /dev/null --max-time 15 "https://www.cdbd.in/login" && { NET_OK=1; break; }
  echo "  네트워크 시도 $attempt/5 실패, 15초 후 재시도"
  /bin/sleep 15
done
[ "$NET_OK" = 1 ] || fail "cdbd.in 도달 불가(네트워크) — 5회 재시도 후에도 실패"

echo "PREFLIGHT OK"
exit 0
