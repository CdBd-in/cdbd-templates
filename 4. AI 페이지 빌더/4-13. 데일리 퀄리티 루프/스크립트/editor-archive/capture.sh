#!/bin/bash
# CdBd 에디터 아카이브 캡처 — 미리보기 전체(스티치) + 에디터 화면 전체
export BROWSE_STATE_FILE=/tmp/browse-arch-state.json
B="$HOME/.claude/skills/gstack/browse/dist/browse"
ID="$1"
OUT=/tmp/arch/out
SEG=/tmp/arch/seg
BASE="https://cdbd-client-git-ai-makevu-s-team.vercel.app"
j(){ $B js "$1" 2>/dev/null | tail -1; }
log(){ echo "[$ID] $*"; }

$B goto "$BASE/editor/$ID" >/dev/null 2>&1
ok=0
for i in $(seq 1 20); do
  sleep 4
  U=$($B url 2>/dev/null)
  case "$U" in *"/editor/$ID"*) ;; *) continue;; esac
  R=$(j "document.querySelector('div.absolute.inset-0.overflow-y-scroll')?'Y':'N'")
  [ "$R" = "Y" ] && { ok=1; break; }
done
[ "$ok" = "1" ] || { log "FAIL open ($($B url))"; echo "$ID FAIL_OPEN" >> /tmp/arch/status.txt; exit 1; }
sleep 6

$B viewport 1680x1500 --scale 1 >/dev/null 2>&1; sleep 3

# 카드 보드 높이 측정 → 필요하면 뷰포트 키움
NEED=$(j "(()=>{const b=[...document.querySelectorAll('button')].find(x=>x.innerText.includes('카드 추가하기'));if(!b)return 1500;const l=b.parentElement.children[1];if(!l)return 1500;return Math.ceil(innerHeight+Math.max(0,l.scrollHeight-l.clientHeight)+24)})()")
case "$NEED" in ''|*[!0-9]*) NEED=1500;; esac
[ "$NEED" -lt 1500 ] && NEED=1500
[ "$NEED" -gt 6000 ] && NEED=6000
if [ "$NEED" -gt 1500 ]; then $B viewport "1680x$NEED" --scale 1 >/dev/null 2>&1; sleep 3; fi

TITLE=$(j "(()=>{const i=document.querySelector('header input,input.text-center');return (i&&i.value)||document.title})()")
NCARD=$(j "(()=>{const b=[...document.querySelectorAll('button')].find(x=>x.innerText.includes('카드 추가하기'));const l=b&&b.parentElement.children[1];return l?l.children.length:0})()")
$B screenshot "$OUT/$ID-editor.png" --viewport >/dev/null 2>&1

# 미리보기 스티치
G=$(j "(()=>{const e=document.querySelector('div.absolute.inset-0.overflow-y-scroll');const r=e.getBoundingClientRect();return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height),e.scrollHeight].join(',')})()")
X=$(echo "$G"|cut -d, -f1); Y=$(echo "$G"|cut -d, -f2); W=$(echo "$G"|cut -d, -f3); H=$(echo "$G"|cut -d, -f4); SH=$(echo "$G"|cut -d, -f5)
rm -f "$SEG"/*.png "$SEG"/offsets.txt
N=$(( (SH + H - 1) / H )); [ "$N" -lt 1 ] && N=1; [ "$N" -gt 40 ] && N=40
for s in $(seq 0 $((N-1))); do
  TY=$(( s*H ))
  j "document.querySelector('div.absolute.inset-0.overflow-y-scroll').scrollTo(0,$TY)" >/dev/null
  sleep 1.2
  AY=$(j "Math.round(document.querySelector('div.absolute.inset-0.overflow-y-scroll').scrollTop)")
  $B screenshot "$SEG/s$s.png" --clip "$X,$Y,$W,$H" >/dev/null 2>&1
  echo "$s $AY" >> "$SEG/offsets.txt"
done
python3 /tmp/arch/stitch.py "$SEG" "$OUT/$ID-preview.png" "$H" || { log "STITCH FAIL"; echo "$ID FAIL_STITCH" >> /tmp/arch/status.txt; exit 1; }
j "document.querySelector('div.absolute.inset-0.overflow-y-scroll').scrollTo(0,0)" >/dev/null
PT=$(j "document.querySelector('div.absolute.inset-0.overflow-y-scroll').innerText.replace(/\s+/g,' ').slice(0,400)")
echo "$ID|$TITLE|$NCARD|$SH|$NEED|$PT" >> /tmp/arch/meta.txt
echo "$ID OK cards=$NCARD prevH=$SH seg=$N" >> /tmp/arch/status.txt
log "OK cards=$NCARD prevH=$SH seg=$N"
