(() => {
  // 프리셋 어드민(/admin/ai/presets) fiber에서 전체 목록을 찾아 window.__presets 에 둔다 — 'ok:<개수>' | 'none'
  const fiberOf = (el) => { const k = Object.keys(el).find((k) => k.startsWith("__reactFiber$")); return k ? el[k] : null; };
  let best = null;
  for (const el of document.querySelectorAll('div,main,section,table')) {
    let n = fiberOf(el), d = 0;
    while (n && d < 15) {
      const p = n.memoizedProps;
      if (p && Array.isArray(p.items) && p.items.length && p.items[0] && p.items[0].preset_key && p.items[0].blocks) {
        if (!best || p.items.length > best.length) best = p.items;
      }
      n = n.return; d++;
    }
  }
  if (!best) return 'none';
  window.__presets = best; return 'ok:' + best.length;
})()
