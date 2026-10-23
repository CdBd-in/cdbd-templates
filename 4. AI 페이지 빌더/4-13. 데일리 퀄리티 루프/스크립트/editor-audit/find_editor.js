(() => {
  // 에디터 fiber에서 editor 객체를 찾아 window.__ed 에 둔다 — 'ok:<JSON 길이>:<카드 수>' | 'loading' | 'none'
  const fiberOf = (el) => { const k = Object.keys(el).find((k) => k.startsWith("__reactFiber$")); return k ? el[k] : null; };
  for (const el of document.querySelectorAll('div')) {
    let n = fiberOf(el), d = 0;
    while (n && d < 8) {
      const p = n.memoizedProps;
      if (p && p.editor && p.editor.theme && (p.editor.blocks || p.editor.pages)) {
        const e = p.editor;
        const cnt = (e.blocks || []).length + (e.pages || []).reduce((s, pg) => s + ((pg.blocks || []).length), 0);
        if (!cnt) return 'loading';
        window.__ed = e; return 'ok:' + JSON.stringify(e).length + ':' + cnt;
      }
      n = n.return; d++;
    }
  }
  return 'none';
})()
