(() => {
window.__pageLabels=()=>[...document.querySelectorAll("*")].filter(e=>e.children.length===0&&/^\d+$/.test(e.textContent.trim())&&String(e.className).includes('text-xs')&&e.getBoundingClientRect().width>0&&e.getBoundingClientRect().x<200);
window.__openPanel=function(){
 if(window.__pageLabels().length) return 'already';
 const els=[...document.querySelectorAll('*')].filter(e=>{const r=e.getBoundingClientRect();return r.x<40&&r.y>100&&r.y<220&&r.width>0&&r.width<80&&r.height>0});
 for(const e of els){const fn=window.__cdbd.onClickOf(e,4);if(fn){fn({target:document.body,stopPropagation(){},preventDefault(){}});return 'opened';}}
 return 'no-opener';};
window.__gotoPage3=function(N){
 var lbl=window.__pageLabels().find(e=>e.textContent.trim()===String(N));
 if(!lbl)return "no-lbl-"+N;
 var f=window.__cdbd.fiberOf(lbl),d=0;
 while(f&&d<4){var oc=f.memoizedProps&&f.memoizedProps.onClick;if(typeof oc==="function"&&/menu-overlay/.test(oc.toString())){oc({target:document.body,stopPropagation(){},preventDefault(){}});return "switched-"+N;}f=f.return;d++;}
 return "no-handler-"+N;};
return "ok";
})()
