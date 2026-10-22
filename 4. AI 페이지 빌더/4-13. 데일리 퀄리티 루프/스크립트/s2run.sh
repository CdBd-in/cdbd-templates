#!/bin/bash
# 사용: s2run.sh <사례ID> "<설명>"   (이미 로그인된 browse 세션 전제)
# 생성 화면 → 확인 화면들 → 첫 시안 → 내용 채우기(텍스트=다음 · 이미지=이건 없어요) → 마지막 확인 → 3안 → 시안A → 무드 → 에디터 → 프리뷰 캡처
B="$HOME/.claude/skills/gstack/browse/dist/browse"
# 🔒 격리 세션 (2026-10-22) — 리서치 등 다른 browse 작업과 데몬을 공유하면
#    S2가 엉뚱한 사이트를 CdBd로 착각해 런이 통째로 무효가 된다 (무효런 Z1 참조)
export BROWSE_STATE_FILE="${BROWSE_STATE_FILE:-/tmp/browse-s2-state.json}"
ID="$1"; DESC="$2"
VAULT="${CDBD_VAULT:-/Users/designer/Documents/GitHub/design/cdbd-templates}"
AR="${S2_AR:-$VAULT/4. AI 페이지 빌더/4-13. 데일리 퀄리티 루프/아카이브/$(date +%Y-%m-%d)/s2}"
mkdir -p "$AR" /tmp/segcap
LOG="$AR/$ID-log.txt"; [ -z "$RESUME" ] && : > "$LOG"
T0=$(date +%s)
log(){ echo "[$(( $(date +%s)-T0 ))s] $*" | tee -a "$LOG"; }
ref(){ $B snapshot -i 2>/dev/null | grep -E "\[button\] \"$1\"" | grep -v disabled | head -1 | grep -oE '@e[0-9]+' | head -1; }
head2(){ $B js "document.body.innerText.replace(/\\s+/g,' ')" 2>/dev/null | tr -d '\n' | cut -c1-${1:-150}; }
# 세션이 CdBd 밖으로 끌려갔는지 매 단계 확인 — 아니면 즉시 중단(무효 산출물 방지)
guard(){ case "$($B url 2>/dev/null)" in *cdbd-client-git-ai-makevu-s-team.vercel.app*) return 0;;
  *) log "ABORT(세션 이탈): $($B url 2>/dev/null) — 다른 browse 작업과 충돌. 런 무효."; exit 3;; esac; }

if [ -z "$RESUME" ] && [ "${STAGE:-}" != "fill" ]; then
$B goto "https://cdbd-client-git-ai-makevu-s-team.vercel.app/ai/create" >/dev/null 2>&1; sleep 5
TB=$($B snapshot -i 2>/dev/null | grep -E '\[textbox\]' | head -1 | grep -oE '@e[0-9]+' | head -1)
[ -z "$TB" ] && { log "FAIL: 입력칸 없음 ($($B url))"; exit 1; }
$B fill "$TB" "$DESC" >/dev/null 2>&1; sleep 1
guard
$B click "$(ref '보내기')" >/dev/null 2>&1; sleep 6
log "설명 확인: $(head2 300)"

# 확인 화면들 → 시안 생성 시작까지
for i in $(seq 1 10); do
  guard
  H=$(head2 200)
  case "$H" in *"시안 제작 중"*|*"첫 번째 시안"*) break;; esac
  case "$H" in *"원페이지"*|*"멀티페이지"*) log "유형: $(echo "$H" | cut -c1-80)";; esac
  case "$H" in *"누구에게"*) log "타겟화면: $($B snapshot -i 2>/dev/null | grep '\[button\]' | grep -vE '이전|다음' | sed 's/.*\[button\] //' | tr '\n' ' ')";; esac
  R=$(ref '다음'); [ -z "$R" ] && { sleep 3; R=$(ref '다음'); }
  [ -z "$R" ] && { log "다음 버튼 없음 → 생성 시작으로 간주, 폴링으로 전환 — $H"; break; }
  $B click "$R" >/dev/null 2>&1; sleep 5
done

# 첫 시안 생성 폴링
OK=0
for i in $(seq 1 12); do
  guard
  [ -n "$(ref '시작하기')" ] && { OK=1; break; }
  sleep 10
done
[ "$OK" = "0" ] && { log "FAIL: 첫 시안 폴링 타임아웃 — 「시작하기」 미등장"; exit 5; }
log "첫 시안 완료"
$B screenshot "$AR/$ID-06-draft1.png" --viewport >/dev/null 2>&1
$B click "$(ref '시작하기')" >/dev/null 2>&1; sleep 4

fi  # STAGE=fill 진입점
if [ -z "$RESUME" ]; then
# 내용 채우기
PREV=""; REP=0; STUCK=0
for i in $(seq 1 25); do
  guard
  R=$(ref '확인했어요'); [ -n "$R" ] && break
  T=$(head2 140); log "Q$i: $T"
  # 지문 = 제목 + 화면의 버튼·입력칸 목록.
  # ⚠️ 제목만 비교하면 한 묶음의 하위 질문들(제목 동일)을 '같은 화면'으로 오판한다 (2026-10-22 오탐 사건)
  H=$( { printf '%s\n' "$T"; $B snapshot -i 2>/dev/null | grep -oE '\[(button|textbox|textarea|combobox|checkbox|radio)\] "[^"]*"'; } | cksum | cut -d' ' -f1 )
  if [ "$H" = "$PREV" ]; then REP=$((REP+1)); else REP=0; fi; PREV="$H"
  if [ "$REP" -ge 2 ]; then
    log "STUCK(같은 화면 3회) — 진행 불가 의심: $($B text 2>/dev/null | grep -oE '[^.]{0,30}입력해 주세요[^.]{0,10}' | head -1)"
    $B screenshot "$AR/$ID-STUCK-q$i.png" --viewport >/dev/null 2>&1
    # 🚫 자동 「항목 지우기」 우회 금지 (2026-10-22) — 멀쩡한 항목을 지워 산출물을 오염시키고,
    #    그 결과(깡통 섹션)를 제품 결함으로 오인해 개발에 전달할 뻔했다. 우회하지 말고 중단·기록만 한다.
    STUCK=1; log "RUN ABORTED: 막다른 길 의심 — 자동 우회 안 함 · 수동 확인 필요"; break
  fi
  R=$(ref '다음'); [ -z "$R" ] && R=$(ref '이건 없어요')
  [ -z "$R" ] && { sleep 3; R=$(ref '다음'); [ -z "$R" ] && R=$(ref '이건 없어요'); }
  [ -z "$R" ] && { log "STOP: 채우기 버튼 없음"; exit 4; }
  $B click "$R" >/dev/null 2>&1; sleep 3
done
fi  # RESUME 끝
[ "${STUCK:-0}" = "1" ] && { log "미완료(막다른 길 의심) — 에디터 미도달 · 채점 제외"; exit 2; }
log "마지막 확인: $($B text 2>/dev/null | sed -n '2p' | cut -c1-600)"
$B screenshot "$AR/$ID-08-final-check.png" --viewport >/dev/null 2>&1
$B click "$(ref '확인했어요')" >/dev/null 2>&1

# 3안 폴링
for i in $(seq 1 12); do sleep 10; [ -n "$(ref '3안 재생성')" ] && break; done
$B snapshot -i 2>/dev/null | grep -E '\[button\] "시안 [ABC]' | sed 's/^ *@e[0-9]* \[button\] //' > "$AR/$ID-3drafts.txt"
log "3안 완료 ($(wc -l < "$AR/$ID-3drafts.txt")안)"
$B screenshot "$AR/$ID-10-3drafts.png" --viewport >/dev/null 2>&1
A=$($B snapshot -i 2>/dev/null | grep -E '\[button\] "시안 A' | grep -oE '@e[0-9]+' | head -1)
$B click "$A" >/dev/null 2>&1; sleep 2
$B click "$(ref '다음')" >/dev/null 2>&1; sleep 5
log "무드: $(head2 120) | 선택=$($B snapshot -i 2>/dev/null | grep -E 'pressed|selected' | head -2 | tr '\n' ' ')"
$B click "$(ref '다음')" >/dev/null 2>&1

# 에디터 도착 폴링
for i in $(seq 1 12); do sleep 10; case "$($B url 2>/dev/null)" in *editor*) break;; esac; done
URL=$($B url 2>/dev/null); log "에디터: $URL"
sleep 12
SC="document.querySelector('div.absolute.inset-0.overflow-y-scroll')"
SH=$($B js "$SC?$SC.scrollHeight:0" 2>/dev/null)
N=$(( (SH + 729) / 730 )); [ "$N" -lt 1 ] && N=1; [ "$N" -gt 8 ] && N=8
rm -f /tmp/segcap/ed_*.png
for s in $(seq 0 $((N-1))); do
  Y=$(( s*730 )); MAX=$(( SH-780 )); [ "$MAX" -lt 0 ] && MAX=0; [ "$Y" -gt "$MAX" ] && Y=$MAX
  $B js "$SC.scrollTo(0,$Y)" >/dev/null 2>&1; sleep 1.5
  $B screenshot "/tmp/segcap/ed_$s.png" --clip 96,120,390,780 >/dev/null 2>&1
done
python3 - "$AR/$ID-12-editor-preview.png" "$N" <<'PY'
import sys; from PIL import Image
out, n = sys.argv[1], int(sys.argv[2])
ims=[Image.open(f'/tmp/segcap/ed_{i}.png') for i in range(n)]
c=Image.new('RGB',(ims[0].width,sum(i.height for i in ims)),'white'); y=0
for im in ims: c.paste(im,(0,y)); y+=im.height
c.save(out)
PY
$B js "$SC?$SC.innerText:''" 2>/dev/null > "$AR/$ID-preview-text.txt"
log "완료 — 프리뷰 높이 ${SH}px · ${N}세그 · 총 $(( $(date +%s)-T0 ))초"
