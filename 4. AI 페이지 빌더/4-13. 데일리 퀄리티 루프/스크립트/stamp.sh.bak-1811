#!/bin/zsh
# 데일리 퀄리티 루프 — 단계 시각 도장 (4-13 §6-6)
# 사용: stamp.sh <단계명> [start|end]
#   예) stamp.sh R start / stamp.sh R end
# 결과: 아카이브/YYYY-MM-DD/timeline.tsv  (단계 \t start|end \t 시각 \t epoch)
# 🔑 리포트의 소요 시간은 이 파일 값만 쓴다(체감·추정 금지 · §0 규칙 12).
set -u
LOOP="/Users/designer/Documents/GitHub/design/cdbd-templates/4. AI 페이지 빌더/4-13. 데일리 퀄리티 루프"
DAY="$(date +%F)"
OUT="$LOOP/아카이브/$DAY/timeline.tsv"
mkdir -p "$LOOP/아카이브/$DAY"
STAGE="${1:?단계명 필요 (전처리|S3|R|S1|S2|P|리포트)}"
EDGE="${2:-start}"
[ -s "$OUT" ] || printf '단계\t구분\t시각\tepoch\n' > "$OUT"
printf '%s\t%s\t%s\t%s\n' "$STAGE" "$EDGE" "$(date '+%F %T')" "$(date +%s)" >> "$OUT"
tail -1 "$OUT"
