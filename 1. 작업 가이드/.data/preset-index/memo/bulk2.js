(()=>{
const MEMO0=window.__MEMO||{};
const ONLY=window.__only||null; const MEMO=ONLY?Object.fromEntries(Object.entries(MEMO0).filter(([k])=>ONLY.includes(k))):MEMO0;
window.__bulk={done:0,skip:0,fail:[],total:Object.keys(MEMO).length,finished:false};
(async()=>{
  const r=await fetch('/api/ai/presets'); const j=await r.json(); const cur={}; for(const p of j.data.items) cur[p.preset_key]=p;
  for(const k of Object.keys(MEMO)){
    const p=cur[k]; if(!p){window.__bulk.fail.push([k,'missing']);continue;}
    if((p.notes||'')===MEMO[k]){window.__bulk.skip++;continue;}
    try{
      const res=await fetch('/api/ai/presets/'+k,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.assign({notes:MEMO[k],layout_styles:p.layout_styles},(typeof p.title_variant==='string')?{title_variant:p.title_variant}:{}))});
      if(res.status!==200){window.__bulk.fail.push([k,res.status,(await res.text()).slice(0,200)]);} else window.__bulk.done++;
    }catch(e){window.__bulk.fail.push([k,String(e)]);}
    await new Promise(s=>setTimeout(s,120));
  }
  window.__bulk.finished=true;
})();
return 'started '+Object.keys(MEMO).length;
})()