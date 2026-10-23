#!/bin/bash
# 에디터 자동 검사 한 번에 — 덤프 → 검사 → 리포트 (2026-10-23)
# 사용: run.sh <출력폴더> <에디터ID> [<에디터ID> …]
#   프리셋 목록은 <출력폴더>/presets.json 이 없을 때만 새로 받는다(하루 1번이면 충분)
HERE="$(cd "$(dirname "$0")" && pwd)"; OUT="$1"; shift
[ -n "$OUT" ] && [ $# -gt 0 ] || { echo "사용: run.sh <출력폴더> <에디터ID> …"; exit 1; }
mkdir -p "$OUT"
[ -s "$OUT/presets.json" ] || "$HERE/dump.sh" --presets "$OUT" || echo "⚠️ 프리셋 목록 없음 — 원본 대조 체크는 미측정"
PR=(); [ -s "$OUT/presets.json" ] && PR=(--presets "$OUT/presets.json")
for ID in "$@"; do
  "$HERE/dump.sh" "$ID" "$OUT" || { echo "$ID 덤프 실패 — 검사 미측정"; continue; }
  python3 "$HERE/audit.py" "$OUT/$ID-editor.json" "${PR[@]}" --md "$OUT/$ID-audit.md" --json "$OUT/$ID-audit.json"
  echo
done
