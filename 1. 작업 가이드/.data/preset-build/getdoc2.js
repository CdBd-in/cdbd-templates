window.__getDoc=function(){function scan(el){var f=window.__cdbd.fiberOf(el);for(var d=0;d<80&&f;d++){var s=f.memoizedState,i=0;while(s&&i<300){var m=s.memoizedState;if(m&&m.loadable&&m.loadable.contents&&m.loadable.contents.present&&Array.isArray(m.loadable.contents.present.pages))return m.loadable.contents.present;s=s.next;i++;}f=f.return;}return null;}
var cands=[].concat(window.__cdbd.boardRows(),[...document.querySelectorAll('button')].filter(b=>/프리셋|URL|저장|카드 추가/.test(b.textContent)).slice(0,6),[...document.querySelectorAll('[contenteditable=true]')].slice(0,3),[...document.querySelectorAll('div')].filter(d=>d.getBoundingClientRect().x>500&&d.getBoundingClientRect().width>200).slice(0,20));
for(var c of cands){try{var r=scan(c);if(r)return r;}catch(e){}}return null;};
'ok'
