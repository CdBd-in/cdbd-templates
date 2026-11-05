#!/bin/bash
# 멀티페이지 에디터 — 왼쪽 썸네일을 차례로 눌러 장마다 미리보기를 이어 붙인다(읽기만 · 편집 ❌)
# 사용: capture-pages.sh <에디터ID>   → $S2_AR/archive/<ID>-preview-p<N>.png
export BROWSE_STATE_FILE="${BROWSE_STATE_FILE:-/tmp/browse-s2-state.json}"
B="${S2_BROWSE_BIN:-$HOME/.claude/skills/gstack/browse/dist/browse}"
ID="$1"; AR="${S2_AR:-/tmp/arch}"; OUT="$AR/archive"; HERE="$(cd "$(dirname "$0")" && pwd)"; mkdir -p "$OUT"
BASE="${CDBD_BASE:-https://cdbd-client-git-ai-makevu-s-team.vercel.app}"
j(){ "$B" js "$1" </dev/null 2>/dev/null | tail -1; }
case "$("$B" url </dev/null 2>/dev/null)" in *"/editor/$ID"*) ;; *) "$B" goto "$BASE/editor/$ID" </dev/null >/dev/null 2>&1; sleep 8;; esac
"$B" viewport 1680x1500 </dev/null >/dev/null 2>&1; sleep 3
N=$(j "(()=>{const m=document.body.innerText.match(/\d+\s*\/\s*(\d+)\s*페이지/);return m?m[1]:1})()")
echo "[$ID] 페이지 $N장"
for k in $(seq 1 "$N"); do
  R=$(j "(()=>{const lab=[...document.querySelectorAll('div,span,p')].filter(e=>e.offsetParent&&e.children.length===0&&(e.innerText||'').trim()==='$k'&&e.getBoundingClientRect().left<200&&e.getBoundingClientRect().top>150)[0];if(!lab)return 'nolabel';lab.scrollIntoView({block:'center'});const r=lab.getBoundingClientRect();const t=document.elementFromPoint(r.left+r.width/2,r.top-60);if(!t)return 'nothumb';t.click();return 'ok'})()")
  sleep 2.5
  G=$(j "(()=>{const e=document.querySelector('div.absolute.inset-0.overflow-y-scroll');if(!e)return '';const r=e.getBoundingClientRect();return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height),e.scrollHeight].join(',')})()")
  [ -n "$G" ] || { echo "[$ID] p$k 미리보기 없음($R)"; continue; }
  X=$(echo "$G"|cut -d, -f1); Y=$(echo "$G"|cut -d, -f2); W=$(echo "$G"|cut -d, -f3); H=$(echo "$G"|cut -d, -f4); SH=$(echo "$G"|cut -d, -f5)
  SEG="$OUT/seg-$ID-p$k"; mkdir -p "$SEG"; rm -f "$SEG"/*.png "$SEG"/offsets.txt
  NS=$(( (SH + H - 1) / H )); [ "$NS" -lt 1 ] && NS=1; [ "$NS" -gt 20 ] && NS=20
  for s in $(seq 0 $((NS-1))); do
    j "document.querySelector('div.absolute.inset-0.overflow-y-scroll').scrollTo(0,$((s*H)))" >/dev/null; sleep 1
    AY=$(j "Math.round(document.querySelector('div.absolute.inset-0.overflow-y-scroll').scrollTop)")
    "$B" screenshot "$SEG/s$s.png" --clip "$X,$Y,$W,$H" </dev/null >/dev/null 2>&1; echo "$s $AY" >> "$SEG/offsets.txt"
  done
  python3 "$HERE/stitch.py" "$SEG" "$OUT/$ID-preview-p$k.png" "$H" >/dev/null && echo "[$ID] p$k OK ($R · h=$SH)"
  j "JSON.stringify(document.querySelector('div.absolute.inset-0.overflow-y-scroll').innerText)" > "$OUT/$ID-preview-text-p$k.json"
done
"$B" viewport 1440x900 </dev/null >/dev/null 2>&1
