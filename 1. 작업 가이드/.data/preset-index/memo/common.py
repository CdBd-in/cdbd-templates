import os
import json, re
VAULT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
IDX = VAULT + "/1. 작업 가이드/.data/preset-index/preset-index.json"

def lex_texts(c):
    """Lexical JSON string -> list of paragraph strings"""
    if not c: return []
    try: d = json.loads(c) if isinstance(c, str) else c
    except Exception: return [str(c)]
    out = []
    def walk(n, buf):
        t = n.get('type')
        if t == 'text': buf.append(n.get('text', ''))
        elif t == 'linebreak': buf.append('\n')
        for ch in n.get('children', []) or []: walk(ch, buf)
    for p in (d.get('root', {}).get('children', []) or []):
        buf = []; walk(p, buf); out.append(''.join(buf))
    return out

def block_texts(b):
    """all visible placeholder texts of one admin block, in order"""
    t = b.get('type'); T = []
    if t in ('text', 'button'): T += lex_texts(b.get('content'))
    if t == 'multiCard':
        for it in (b.get('multiCard') or {}).get('items', []) or []:
            if it.get('type') in ('text', 'button'): T += lex_texts(it.get('content'))
    if t == 'profile':
        pr = b.get('profile') or {}
        T += lex_texts(pr.get('name')) + lex_texts(pr.get('description'))
    if t == 'qna':
        q = b.get('qna') or {}
        T += [q.get('title', '')] if q.get('title') else []
        for it in q.get('list', []) or []:
            T.append(it.get('question', ''))
            T += [o.get('text', '') for o in it.get('options', []) or []]
    if t == 'reservation':
        r = b.get('reservation') or {}; T += [r.get('title', '')]
    if t == 'menu':
        T += [i.get('label', '') for i in (b.get('menu') or {}).get('items', []) or []]
    if t == 'location':
        T += [(b.get('location') or {}).get('address', '')]
    return [x for x in (s.strip() for s in T) if x]

def admin_to_name(key):
    k = key.split('/')
    if k[0] == 'hdr': return 'header-' + k[1]
    if k[0] == 'ftr': return 'footer-' + k[1]
    if k[0] == 'title': return 'title-' + k[1]
    return f"{k[2]}-{k[1]}-{k[3]}"

def name_to_admin(name):
    m = re.match(r'(header|footer|title)-(\d+)$', name)
    if m: return {'header': 'hdr', 'footer': 'ftr', 'title': 'title'}[m.group(1)] + '/' + m.group(2)
    purpose, style, nn = name.rsplit('-', 2)
    return f"sec/{style}/{purpose}/{nn}"
