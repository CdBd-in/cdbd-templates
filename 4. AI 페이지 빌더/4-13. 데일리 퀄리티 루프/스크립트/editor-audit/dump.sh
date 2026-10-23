#!/bin/bash
# 에디터 데이터 덤프 — audit.py 입력 만들기 (2026-10-23)
# 사용: dump.sh <에디터ID> <출력폴더>     → <출력폴더>/<ID>-editor.json
#       dump.sh --presets <출력폴더>      → <출력폴더>/presets.json (프리셋 어드민 전체 목록 · 원본 대조용)
# 환경: BROWSE_STATE_FILE = 격리 세션(필수 권장) · CDBD_BASE = 기본 프리뷰 도메인(S2가 로그인한 곳)
#       www.cdbd.in 에디터를 볼 땐 CDBD_BASE=https://www.cdbd.in (그 도메인에 로그인돼 있어야 함)
B="$HOME/.claude/skills/gstack/browse/dist/browse"
BASE="${CDBD_BASE:-https://cdbd-client-git-ai-makevu-s-team.vercel.app}"
HERE="$(cd "$(dirname "$0")" && pwd)"
j(){ $B js "$1" 2>/dev/null | tail -1; }

if [ "$1" = "--presets" ]; then
  OUT="$2"; mkdir -p "$OUT"; P="https://cdbd-client-git-ai-makevu-s-team.vercel.app"
  $B goto "$P/admin/ai/presets" >/dev/null 2>&1
  R=none; for i in $(seq 1 15); do sleep 3; R=$(j "$(cat "$HERE/find_presets.js")"); case "$R" in ok:*) break;; esac; done
  case "$R" in ok:*) ;; *) echo "FAIL presets ($R · $($B url))"; exit 2;; esac
  j "JSON.stringify(window.__presets)" > "$OUT/presets.json"
  python3 -c "import json,sys;print('presets',len(json.load(open(sys.argv[1]))))" "$OUT/presets.json" || exit 2
  exit 0
fi

ID="$1"; OUT="$2"; [ -n "$ID" ] && [ -n "$OUT" ] || { echo "사용: dump.sh <에디터ID> <출력폴더>"; exit 1; }
mkdir -p "$OUT"
case "$($B url 2>/dev/null)" in *"/editor/$ID"*) ;; *) $B goto "$BASE/editor/$ID" >/dev/null 2>&1;; esac
sleep 3; case "$($B url 2>/dev/null)" in *"/login"*) echo "FAIL editor $ID — 로그인 필요($BASE)"; exit 3;; esac
# 다 불러올 때까지 기다린다 — 같은 길이가 두 번 연속 나오면 확정(불러오는 중 덤프 방지)
R=none; PREV=""
for i in $(seq 1 25); do
  sleep 3; R=$(j "$(cat "$HERE/find_editor.js")")
  case "$R" in ok:*) [ "$R" = "$PREV" ] && break; PREV="$R";; esac
done
case "$R" in ok:*) ;; *) echo "FAIL editor $ID ($R · $($B url))"; exit 2;; esac
j "JSON.stringify(window.__ed)" > "$OUT/$ID-editor.json"
python3 - "$OUT/$ID-editor.json" "$ID" <<'PY' || exit 2
import json, sys
d = json.load(open(sys.argv[1]))
if str(d.get('id')) != sys.argv[2]:
    import os; os.remove(sys.argv[1])
    sys.exit(f"FAIL editor {sys.argv[2]} — 열리지 않음(다른 페이지 {d.get('id')}가 열림 · 지워졌거나 권한 없음)")
n = len(d.get('blocks') or [b for p in d.get('pages') or [] for b in p.get('blocks') or []])
print(f"editor {d['id']} 카드 {n} → {sys.argv[1]}")
PY
