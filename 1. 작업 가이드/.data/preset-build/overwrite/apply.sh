#!/bin/bash
# 섹션 원본(마스터 에디터 페이지) 여백 고치기 + 고치기 전후 미리보기 픽셀 비교 (2026-10-23)
# usage: MID=<마스터 번호> apply.sh <페이지 번호> <spec.json> <tag>
# 결과: check=OK → mutated → after=after-ok → PIXDIFF NONE 이어야 정상 (보이는 간격을 바꾸지 않는 수정일 때)
# spec.json = [{"id":..,"before":"T R B L","after":"T R B L"}, ...]  (padding only)
export BROWSE_STATE_FILE="${BROWSE_STATE_FILE:-/tmp/browse-preset-state.json}"
B="$HOME/.claude/skills/gstack/browse/dist/browse"
N="$1"; SPEC="$2"; TAG="$3"
HERE="$(cd "$(dirname "$0")" && pwd)"; T=/tmp/preset-overwrite; mkdir -p $T
cp "$HERE/mclick.js" "$HERE/nav.js" $T/; cp "$HERE/../../../../.claude/skills/cdbd-card-automation/card-driver.js" $T/
SH=${SHOTS:-$T/shots}; mkdir -p $SH
MID="${MID:?MID 필요}"
case "$($B url)" in *"/editor/$MID"*) ;; *)
  $B goto "https://cdbd-client-git-ai-makevu-s-team.vercel.app/editor/$MID" >/dev/null 2>&1
  for i in $(seq 1 15); do sleep 2; R=$($B js "document.querySelector('div.absolute.inset-0.overflow-y-scroll')?'Y':'N'" 2>/dev/null | tail -1); [ "$R" = "Y" ] && break; done
  sleep 6;;
esac
case "$($B url)" in *"/editor/$MID"*) ;; *) echo "ABORT not on editor $MID: $($B url)"; exit 1;; esac
$B eval $T/card-driver.js >/dev/null; $B eval $T/mclick.js >/dev/null; $B eval $T/nav.js >/dev/null
$B js "window.__n4=s=>{const a=String(s||'0px').trim().split(/\s+/).map(v=>parseFloat(v)||0);if(a.length===1)return [a[0],a[0],a[0],a[0]];if(a.length===2)return [a[0],a[1],a[0],a[1]];if(a.length===3)return [a[0],a[1],a[2],a[1]];return a.slice(0,4)};'ok'" >/dev/null
SPECJS=$(python3 -c "import json;print(json.dumps(json.load(open('$SPEC'))))")
$B js "window.__spec=$SPECJS; 'ok'" >/dev/null
OP=$($B js "window.__openPanel()" | tail -1); sleep 2
G=$($B js "window.__gotoPage3($N)" | tail -1); sleep 3
$B js "document.elementFromPoint(880,400).click(); 'c'" >/dev/null; sleep 2
CHK=$($B js "(()=>{const rows=window.__cdbd.boardRows().map(r=>window.__cdbd.blockOfRow(r));window.__ids0=rows.map(b=>b.id).join(',');for(const s of __spec){const b=rows.find(x=>x.id===s.id);if(!b)return 'ABORT missing '+s.id.slice(0,8)+' rows='+rows.map(x=>x.id.slice(0,8)).join(',');const cur=__n4(b.style.padding).join(' ');if(cur!==__n4(s.before).join(' '))return 'ABORT before-mismatch '+s.id.slice(0,8)+' cur='+cur;}return 'OK '+rows.length})()" | tail -1)
echo "panel=$OP goto=$G check=$CHK"
case "$CHK" in OK*) ;; *) exit 1;; esac
SC="document.querySelector('div.absolute.inset-0.overflow-y-scroll')"
PR=$($B js "(()=>{const r=$SC.getBoundingClientRect();return [r.x,r.y,r.width,r.height].map(Math.round).join(',')})()" | tail -1)
SHT=$($B js "$SC.scrollHeight" | tail -1); CH=$($B js "$SC.clientHeight" | tail -1)
OFFS=$(python3 -c "h=$SHT;c=$CH;import sys;o=list(range(0,max(1,h-c+1),max(100,c-56)));o=o+[max(0,h-c)] if (h>c and o[-1]!=max(0,h-c)) else o;print(' '.join(map(str,o)))")
shoot(){ for o in $OFFS; do $B js "$SC.scrollTo(0,$o)" >/dev/null; sleep 0.8; $B screenshot $SH/$TAG-$1-$o.png --clip "$PR" >/dev/null 2>&1; done; $B js "$SC.scrollTo(0,0)" >/dev/null; }
shoot before
MUT=$($B js "(()=>{const rows=window.__cdbd.boardRows().map(r=>window.__cdbd.blockOfRow(r));const f=a=>a.map(v=>v+'px').join(' ');const out=[];for(const s of __spec){const b=rows.find(x=>x.id===s.id);b.style.padding=f(__n4(s.after));out.push(s.id.slice(0,6)+'='+b.style.padding)}return 'mutated '+out.join(' | ')})()" | tail -1)
echo "$MUT"
$B js "JSON.stringify(window.__cdbd.reorderCard(0,1))" >/dev/null; sleep 2.5
$B js "JSON.stringify(window.__cdbd.reorderCard(1,0))" >/dev/null; sleep 3
AFT=$($B js "(()=>{const rows=window.__cdbd.boardRows().map(r=>window.__cdbd.blockOfRow(r));if(rows.map(b=>b.id).join(',')!==window.__ids0)return 'ORDER-CHANGED';const bad=__spec.filter(s=>__n4(rows.find(x=>x.id===s.id).style.padding).join(' ')!==__n4(s.after).join(' '));return bad.length?'VALUE-BAD '+bad.map(s=>s.id.slice(0,8)).join(','):'after-ok'})()" | tail -1)
echo "after=$AFT"
SHT2=$($B js "$SC.scrollHeight" | tail -1)
[ "$SHT" = "$SHT2" ] || echo "WARN scrollHeight $SHT -> $SHT2"
shoot after
python3 - "$SH" "$TAG" $OFFS <<'EOF'
import sys
from PIL import Image, ImageChops
d,t=sys.argv[1],sys.argv[2]; tot=0; worst=0; boxes=[]
for o in sys.argv[3:]:
    a=Image.open(f'{d}/{t}-before-{o}.png').convert('RGB'); b=Image.open(f'{d}/{t}-after-{o}.png').convert('RGB')
    if a.size!=b.size: print('PIXDIFF size'); sys.exit()
    df=ImageChops.difference(a,b); bb=df.getbbox()
    if bb:
        n=sum(1 for p in df.getdata() if max(p)>16); tot+=n; boxes.append((o,bb,n))
print('PIXDIFF', 'NONE' if not boxes else f'shots={len(sys.argv)-3} diffs={boxes} px>16={tot}')
EOF
