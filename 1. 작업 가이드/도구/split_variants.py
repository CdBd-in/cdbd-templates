import re, json, sys
h = open('/tmp/freelancer.html', encoding='utf-8').read()

def extract_div(html, start):
    """start = index of '<div' opening; return (fragment, end_index) via depth matching"""
    i, depth = start, 0
    tag_re = re.compile(r'<(/?)(\w[\w-]*)([^>]*?)(/?)>')
    while i < len(html):
        m = tag_re.search(html, i)
        if not m: break
        closing, tag, attrs, selfclose = m.groups()
        if tag.lower() == 'div' and not selfclose:
            depth += -1 if closing else 1
            if depth == 0:
                return html[start:m.end()], m.end()
        i = m.end()
    return html[start:], len(html)

ids = re.findall(r'시안\s+(\w+)\s*═*\s*-->\s*<div id="(\w+)"', h)
out = {}
for label, vid in ids:
    m = re.search(r'<div id="%s"' % re.escape(vid), h)
    frag, _ = extract_div(h, m.start())
    cards = re.findall(r'<!-- 카드: ([^>]*?) -->', frag)
    out[vid] = {'label': label, 'len': len(frag), 'cards': cards}
    open(f'/tmp/variant-{vid}.html', 'w', encoding='utf-8').write(frag)

for vid, d in out.items():
    print(f"{vid:4s} len={d['len']:7d} 카드={len(d['cards']):3d}")
json.dump({k: v['cards'] for k, v in out.items()}, open('/tmp/variant-cards.json','w'), ensure_ascii=False, indent=1)
