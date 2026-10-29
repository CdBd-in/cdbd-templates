#!/bin/bash
# usage: savepreset.sh <pageN> <style(미니멀|에디토리얼|볼드)> <purpose(나열 …)> <key> <memo>
B="$HOME/.claude/skills/gstack/browse/dist/browse"
N="$1"; ST="$2"; PU="$3"; KEY="$4"; MEMO="$5"
$B js "window.__openPanel()" >/dev/null; sleep 1.2
r=$($B js "window.__gotoPage2($N)" | tail -1); [ "$r" = "switched-$N" ] || { echo "FAIL goto $N: $r"; exit 1; }
sleep 2; $B js "window.__closePanel()" >/dev/null; sleep 1.5
$B js "(function(){var b=[...document.querySelectorAll('button')].find(e=>e.textContent.trim().startsWith('프리셋 설정')&&e.getBoundingClientRect().y<80);b.click();return 'ok'})()" >/dev/null; sleep 1.3
$B js "(function(){var b=[...document.querySelectorAll('button')].find(e=>e.textContent.trim()==='지금 내용을 프리셋으로 저장');return b?window.__press(b):'no-item'})()" >/dev/null; sleep 2
$B js "window.__setStyles(['$ST'])" >/dev/null; sleep 0.8
$B js "window.__openPurpose()" >/dev/null; sleep 1
$B js "(function(){var o=[...document.querySelectorAll('button')].find(e=>e.textContent.trim()==='$PU'&&e.getBoundingClientRect().height>0&&e.getBoundingClientRect().y>480);return o?window.__press(o):'no-opt'})()" >/dev/null; sleep 1
$B js "window.__setKey('$KEY')" >/dev/null; sleep 1.5
ST_NOW=$($B js "'cards='+(document.body.innerText.match(/미리보기 \((\d+)\)/)||[])[1]+' key='+window.__keyInput().value+' status='+window.__keyStatus()+' styles='+window.__styleState()+' purpose='+[...document.querySelectorAll('button')].find(e=>{var r=e.getBoundingClientRect();return r.y>440&&r.y<500&&r.width>300&&String(e.className).includes('justify-between')}).textContent.trim()" | tail -1)
echo "$ST_NOW"
case "$ST_NOW" in *"사용 가능"*) ;; *) echo "ABORT: key not new — not saving"; $B js "(function(){var b=[...document.querySelectorAll('button')].find(e=>e.textContent.trim()==='취소하기');if(b)b.click();return 'cancelled'})()"; exit 2;; esac
$B js "window.__setMemo($(python3 -c 'import json,sys;print(json.dumps(sys.argv[1]))' "$MEMO"))" >/dev/null; sleep 0.5
$B js "(function(){var b=window.__saveBtn();b.click();return 'clicked'})()" >/dev/null; sleep 3
$B js "(function(){var t=[...document.querySelectorAll('*')].filter(e=>e.children.length===0&&/초안 저장됨/.test(e.textContent)).map(e=>e.textContent.trim().slice(0,80));return t.join(' | ')||'no-toast'})()" | tail -1
