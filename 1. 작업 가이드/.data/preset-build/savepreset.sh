#!/bin/bash
# 새 섹션 원본 저장(새 키 전용) — v2 (2026-10-29 · 13호 8건 등록에서 검증)
# usage: savepreset.sh <페이지 번호> <미니멀|에디토리얼|볼드> <목적(나열 …)> <키> <첫 카드 id 앞부분> <카드 수> <memos.json>
#   memos.json = {"<키>": "<메모 전문>"} · 도우미(card-driver·getdoc2·pagepanel·goto·press·modal·overwrite/mclick.js)를 먼저 주입해 둘 것
#   BROWSE_STATE_FILE = 로그인된 격리 세션(필수)
# v1과 다른 점(v1 함정 2건): ① 목적 드롭다운 항목을 「화면 위치」가 아니라 항목 버튼 자체에 포인터 이벤트로 누른다(「위치 안내」가 열기 버튼에 가려 오클릭)
#   ② 키·메모 칸을 저장 창(dialog) 안에서 placeholder로 찾는다(Q&A가 든 섹션은 미리보기 입력칸이 첫 칸이 된다) · 저장 전 페이지(첫 카드·카드 수)와 모든 값 대조 → 하나라도 다르면 취소
B="$HOME/.claude/skills/gstack/browse/dist/browse"
[ -n "$BROWSE_STATE_FILE" ] || { echo "BROWSE_STATE_FILE 없음 — 격리 세션을 지정하세요"; exit 1; }
j(){ $B js "$1" 2>&1 | tail -1; }
N="$1"; ST="$2"; PU="$3"; KEY="$4"; FIRST="$5"; CNT="$6"; MEMOS="$7"
[ -f "$MEMOS" ] || { echo "memos.json 없음: $MEMOS"; exit 1; }
cancel(){ j "(function(){var b=[...document.querySelectorAll('button')].find(e=>e.textContent.trim()==='취소하기'&&e.getBoundingClientRect().width>0);if(b)b.click();return 'cancelled'})()"; }
j "window.__openPanel()" >/dev/null; sleep 1.5
g=$(j "window.__gotoPage2($N)"); sleep 2.5; j "window.__closePanel()" >/dev/null; sleep 2
F=$(j "(function(){var rows=window.__cdbd.boardRows().map(r=>window.__cdbd.blockOfRow(r));return rows.length+':'+(rows[0]?rows[0].id:'none')})()")
echo "goto=$g rows/first=$F"
case "$F" in "$CNT:$FIRST"*) ;; *) echo "ABORT wrong page (expected $CNT:$FIRST)"; exit 1;; esac
j "(function(){var b=[...document.querySelectorAll('button')].find(e=>e.textContent.trim().startsWith('프리셋 설정')&&e.getBoundingClientRect().y<80);b.click();return 'ok'})()" >/dev/null; sleep 1.3
j "(function(){var b=[...document.querySelectorAll('button')].find(e=>e.textContent.trim()==='지금 내용을 프리셋으로 저장');return b?window.__press(b):'no-item'})()" >/dev/null; sleep 2.5
HAS=$(j "(function(){var d=window.__dlg();return d&&/프리셋 저장/.test(d.innerText)?'dlg':'none'})()")
[ "$HAS" = "dlg" ] || { echo "ABORT no dialog"; exit 1; }
j "window.__setStyles(['$ST'])" >/dev/null; sleep 1
j "(function(){var d=window.__dlg();var btn=[...d.querySelectorAll('button')].find(e=>/^(히어로|소개|핵심 정보|스토리|안내 사항|나열|자료|예약|폼|구매|프로모션|위치 안내|문의)$/.test((e.innerText||'').trim())&&String(e.className).includes('h-[38px]'));return btn?window.__mclick(btn):'no-dd'})()" >/dev/null; sleep 1.2
j "(function(){var o=[...document.querySelectorAll('button')].filter(e=>e.childElementCount===0&&(e.innerText||'').trim()==='$PU'&&e.getBoundingClientRect().width>0).pop();if(!o)return 'no-opt';var r=o.getBoundingClientRect();var x=r.x+r.width/2,y=r.y+r.height/2;var op={bubbles:true,cancelable:true,clientX:x,clientY:y,button:0};['pointerdown','mousedown','pointerup','mouseup','click'].forEach(function(ev){o.dispatchEvent(ev.startsWith('pointer')?new PointerEvent(ev,op):new MouseEvent(ev,op));});return 'picked'})()" >/dev/null; sleep 1.2
j "window.__setKey('$KEY')" >/dev/null; sleep 1.5
MEMO_JS=$(python3 -c "import json,sys;m=json.load(open(sys.argv[1]));print(json.dumps(m[sys.argv[2]],ensure_ascii=False))" "$MEMOS" "$KEY") || { echo "ABORT memo for $KEY not in $MEMOS"; cancel; exit 1; }
j "window.__setMemo($MEMO_JS)" >/dev/null; sleep 0.8
ST_NOW=$(j "(function(){var want=$MEMO_JS;var d=window.__dlg();var ta=[...d.querySelectorAll('textarea')].find(t=>/포팅 출처/.test(t.placeholder||''));var t=d.innerText.replace(/\s+/g,' ');var k=t.match(/종류 (섹션 타이틀|섹션|헤더|푸터)/);var ki=[...d.querySelectorAll('input')].find(e=>e.type==='text'&&/^sec\//.test(e.placeholder||''));var key=ki?ki.value:'NO-KEY-INPUT';var btn=[...d.querySelectorAll('button')].find(e=>String(e.className).includes('h-[38px]')&&/^(히어로|소개|핵심 정보|스토리|안내 사항|나열|자료|예약|폼|구매|프로모션|위치 안내|문의)$/.test((e.innerText||'').trim()));var cards=(t.match(/미리보기 \((\d+)\)/)||[])[1];return ['kind='+(k&&k[1]),'styles='+window.__styleState(),'purpose='+(btn&&btn.innerText.trim()),'key='+key,'status='+window.__keyStatus(),'cards='+cards,'memo='+(ta&&ta.value===want?'OK':'BAD')].join(' | ')})()")
WANT_STY="미니멀=$([ "$ST" = 미니멀 ] && echo true || echo false),에디토리얼=$([ "$ST" = 에디토리얼 ] && echo true || echo false),볼드=$([ "$ST" = 볼드 ] && echo true || echo false),공통=false"
EXP="kind=섹션 | styles=$WANT_STY | purpose=$PU | key=$KEY | status=사용 가능 · 새로 저장됩니다 | cards=$CNT | memo=OK"
echo "$ST_NOW"
if [ "$ST_NOW" != "$EXP" ]; then echo "ABORT state mismatch"; echo "expected: $EXP"; cancel; exit 2; fi
j "(function(){var b=window.__saveBtn();if(!b)return 'no-save-btn';if(b.textContent.trim()!=='새 초안으로 생성')return 'not-new:'+b.textContent.trim();b.click();return 'clicked'})()"; sleep 3
T=$(j "(function(){var t=[...document.querySelectorAll('*')].filter(e=>e.children.length===0&&/초안 저장됨/.test(e.textContent)).map(e=>(e.textContent.match(/초안 저장됨: [^ ]+/)||[''])[0]);return t.join(' | ')||'no-toast'})()")
echo "toast=$T"
case "$T" in *"초안 저장됨: $KEY"*) echo "SAVED $KEY";; *) echo "WARN toast mismatch"; exit 4;; esac
