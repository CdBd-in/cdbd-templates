(() => {
window.__mclick = function(el){
  const r=el.getBoundingClientRect(); const x=r.x+r.width/2, y=r.y+r.height/2;
  const t=document.elementFromPoint(x,y)||el; const o={bubbles:true,cancelable:true,clientX:x,clientY:y,button:0};
  ['pointerdown','mousedown','pointerup','mouseup','click'].forEach(ev=>t.dispatchEvent(ev.startsWith('pointer')?new PointerEvent(ev,o):new MouseEvent(ev,o)));
  return Math.round(x)+','+Math.round(y);
};
window.__dlg = () => [...document.querySelectorAll('[role=dialog],.MuiDialog-root,.MuiModal-root')].pop();
window.__layoutState = () => { const d=window.__dlg(); return [...d.querySelectorAll('label')].filter(l=>/^(미니멀|에디토리얼|볼드|공통)$/.test((l.innerText||'').trim())).map(l=>{const cb=l.querySelector('input[type=checkbox]')||document.getElementById(l.htmlFor);return (l.innerText||'').trim()+':'+(cb?cb.checked:'?')}).join(' '); };
return 'ok';
})()
