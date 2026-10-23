#!/bin/bash
# 지금 페이지를 같은 키로 덮어쓰기 — 레이아웃·목적·종류를 원래와 똑같이 맞추고, 메모는 저장 직전에 어드민에서 최신값을 읽어 다시 넣는다 (2026-10-23)
# usage: save.sh <키> <종류:섹션|헤더|푸터> <레이아웃: 미니멀,에디토리얼,볼드,공통 순서로 쉼표> <목적|-> 
# ⚠️ 저장 창 메모 칸은 빈 채로 열리고 그대로 저장하면 기존 메모가 지워진다 → 이 스크립트가 최신 메모를 채운다
export BROWSE_STATE_FILE="${BROWSE_STATE_FILE:-/tmp/browse-preset-state.json}"
B="$HOME/.claude/skills/gstack/browse/dist/browse"
KEY="$1"; KIND="$2"; LAYS="$3"; PURP="$4"
# 최신 메모 읽기 (저장 직전 · 다른 작업이 메모를 쓰는 중일 수 있다)
$B js "window.__memoWant=undefined;fetch('/api/ai/presets').then(r=>r.json()).then(j=>{const p=j.data.items.find(x=>x.preset_key==='$KEY');window.__memoWant=p?(p.notes||''):null}).catch(e=>{window.__memoWant=null});'started'" >/dev/null
for i in 1 2 3 4 5 6; do sleep 1; R=$($B js "typeof window.__memoWant" | tail -1); [ "$R" = "string" ] && break; [ "$R" = "object" ] && { echo "ABORT: 어드민에 키 없음($KEY) — 새 원본이면 savepreset.sh"; exit 1; }; done
[ "$R" = "string" ] || { echo "ABORT: 최신 메모를 못 읽음"; exit 1; }
MEMO="window.__memoWant"
HERE="$(cd "$(dirname "$0")" && pwd)"; mkdir -p /tmp/preset-overwrite; cp "$HERE/mclick.js" /tmp/preset-overwrite/; $B eval /tmp/preset-overwrite/mclick.js >/dev/null
$B js "(()=>{const b=[...document.querySelectorAll('button')].find(e=>(e.innerText||'').trim()==='프리셋 설정'&&e.getBoundingClientRect().y<80);b.click();return 'dd'})()" >/dev/null; sleep 1.5
$B js "(()=>{const el=[...document.querySelectorAll('*')].find(e=>e.childElementCount===0&&(e.innerText||'').trim()==='지금 내용을 프리셋으로 저장'&&e.getBoundingClientRect().width>0);return el?window.__mclick(el):'no-item'})()" >/dev/null; sleep 2.5
HAS=$($B js "(()=>{const d=window.__dlg();return d&&/프리셋 저장/.test(d.innerText)?'dlg':'none'})()" | tail -1)
[ "$HAS" = "dlg" ] || { echo "ABORT no dialog"; exit 1; }
cancel(){ $B js "(()=>{const b=[...document.querySelectorAll('button')].find(b=>(b.innerText||'').trim()==='취소하기'&&b.getBoundingClientRect().width>0);if(b)b.click();return 'cancel'})()" >/dev/null; }
# kind
if [ "$KIND" != "섹션" ]; then
  $B js "(()=>{const d=window.__dlg();const btn=[...d.querySelectorAll('button,[role=button],div')].find(e=>(e.innerText||'').trim()==='섹션'&&String(e.className).includes('h-[38px]'));return btn?window.__mclick(btn):'no-dd'})()" >/dev/null; sleep 1.2
  $B js "(()=>{const b=[...document.querySelectorAll('button')].filter(e=>e.childElementCount===0&&(e.innerText||'').trim()==='$KIND'&&e.getBoundingClientRect().width>0).pop();return b?window.__mclick(b):'no-opt'})()" >/dev/null; sleep 1.5
fi
# layouts — exact match
for L in 미니멀 에디토리얼 볼드 공통; do
  WANT=0; case ",$LAYS," in *",$L,"*) WANT=1;; esac
  CUR=$($B js "(()=>{const l=[...window.__dlg().querySelectorAll('label')].find(l=>(l.innerText||'').trim()==='$L');const c=l&&l.querySelector('input[type=checkbox]');return c&&c.checked?1:0})()" | tail -1)
  if [ "$CUR" != "$WANT" ]; then $B js "(()=>{const l=[...window.__dlg().querySelectorAll('label')].find(l=>(l.innerText||'').trim()==='$L');return window.__mclick(l)})()" >/dev/null; sleep 1.2; fi
done
# purpose
if [ "$PURP" != "-" ]; then
  CURP=$($B js "(()=>{const d=window.__dlg();const btn=[...d.querySelectorAll('button,[role=button],div')].find(e=>/^(히어로|소개|핵심 정보|스토리|안내 사항|나열|자료|예약|폼|구매|프로모션|위치 안내|문의)$/.test((e.innerText||'').trim())&&String(e.className).includes('h-[38px]'));return btn?(btn.innerText||'').trim():'none'})()" | tail -1)
  if [ "$CURP" != "$PURP" ]; then
    $B js "(()=>{const d=window.__dlg();const btn=[...d.querySelectorAll('button,[role=button],div')].find(e=>/^(히어로|소개|핵심 정보|스토리|안내 사항|나열|자료|예약|폼|구매|프로모션|위치 안내|문의)$/.test((e.innerText||'').trim())&&String(e.className).includes('h-[38px]'));return btn?window.__mclick(btn):'no-dd'})()" >/dev/null; sleep 1.2
    $B js "(()=>{const b=[...document.querySelectorAll('button')].filter(e=>e.childElementCount===0&&(e.innerText||'').trim()==='$PURP'&&e.getBoundingClientRect().width>0).pop();return b?window.__mclick(b):'no-opt'})()" >/dev/null; sleep 1.5
  fi
fi
# key
$B js "(()=>{const ki=[...window.__dlg().querySelectorAll('input')].find(e=>e.type==='text');const set=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;set.call(ki,'$KEY');ki.dispatchEvent(new Event('input',{bubbles:true}));ki.dispatchEvent(new Event('change',{bubbles:true}));return ki.value})()" >/dev/null; sleep 2
# memo
$B js "(()=>{const want=$MEMO;const ta=window.__dlg().querySelector('textarea');if(!ta)return 'no-ta';if(ta.value===want)return 'memo-same';const set=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;set.call(ta,want);ta.dispatchEvent(new Event('input',{bubbles:true}));ta.dispatchEvent(new Event('change',{bubbles:true}));return 'memo-set'})()" >/dev/null; sleep 1
# verify state
ST=$($B js "(()=>{const d=window.__dlg();const t=d.innerText.replace(/\s+/g,' ');const lays=[...d.querySelectorAll('label')].filter(l=>/^(미니멀|에디토리얼|볼드|공통)$/.test((l.innerText||'').trim())).filter(l=>{const c=l.querySelector('input[type=checkbox]');return c&&c.checked}).map(l=>(l.innerText||'').trim()).join(',');const k=t.match(/종류 (섹션 타이틀|섹션|헤더|푸터)/);const pbtn=[...d.querySelectorAll('button,[role=button],div')].find(e=>/^(히어로|소개|핵심 정보|스토리|안내 사항|나열|자료|예약|폼|구매|프로모션|위치 안내|문의)$/.test((e.innerText||'').trim())&&String(e.className).includes('h-[38px]'));const key=[...d.querySelectorAll('input')].find(e=>e.type==='text').value;const ex=/이미 있는 프리셋/.test(t);const memo=d.querySelector('textarea').value;return [k?k[1]:'?',lays,pbtn?(pbtn.innerText||'').trim():'-',key,ex?'EXISTING':'NEW',memo===$MEMO?'memo-ok':'memo-BAD'].join('|')})()" | tail -1)
EXP="$KIND|$LAYS|$PURP|$KEY|EXISTING|memo-ok"
echo "state=$ST"
if [ "$ST" != "$EXP" ]; then echo "ABORT state mismatch (expected $EXP)"; cancel; exit 2; fi
$B js "(()=>{const b=[...document.querySelectorAll('button')].find(b=>(b.innerText||'').trim()==='변경사항 저장'&&b.getBoundingClientRect().width>0);if(!b)return 'no';b.click();return 'clicked'})()" >/dev/null; sleep 2
CF=$($B js "(()=>{const d=[...document.querySelectorAll('[role=dialog],.MuiDialog-root')].map(d=>(d.innerText||'').replace(/\s+/g,' ')).find(t=>/이 프리셋에 저장/.test(t));return d||'none'})()" | tail -1)
case "$CF" in *"$KEY 프리셋으로 저장됩니다"*) ;; *) echo "ABORT confirm text: $CF"; cancel; exit 3;; esac
$B js "(()=>{const b=[...document.querySelectorAll('button')].find(b=>(b.innerText||'').trim()==='저장'&&b.getBoundingClientRect().width>0);if(!b)return 'no';b.click();return 'confirmed'})()" >/dev/null; sleep 3
T=$($B js "(document.body.innerText.match(/저장됨: [^\n]{0,40}/)||['no-toast'])[0]" | tail -1)
echo "toast=$T"
[ "$T" = "저장됨: $KEY" ] || { echo "WARN toast mismatch"; exit 4; }
