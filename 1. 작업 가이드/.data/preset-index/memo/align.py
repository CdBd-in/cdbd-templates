import os
import json, re, sys, difflib
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
I = json.load(open(IDX)); P = json.load(open(os.environ.get('PRESETS_JSON','/tmp/presets/presets.json')))
FS = {}
for tok in open(os.environ.get('FIGSIG_TXT', os.path.join(os.path.dirname(os.path.abspath(__file__)),'figsig.txt'))).read().split():
    n, s = tok.rsplit(':', 1) if tok.count(':') else (tok, '')
    FS.setdefault(n, s)
L = {'text':'T','multiCard':'M','divider':'D','gallery':'G','image':'I','button':'B','location':'L','profile':'P',
     'reservation':'R','qna':'Q','menu':'U','sns':'S','youtube':'Y','product':'x'}
def asig(p): return ''.join(L.get(b['type'],'x') for b in p['blocks'] if not b.get('disabled'))
DESC = re.compile(r'(메인 |서브 |프로필 |디테일 |배경 )?(이미지|비주얼)( · 어둡게)?|로고|지도 임베드|SNS 아이콘|메뉴 아이콘|아이콘|\(그리드\)|x\d|\(스펙 포함\)|\(표형\)|\(아이콘형\)|\(인라인\)')
def norm(s): return re.sub(r'\s+', ' ', re.sub(r'[|·・,()]', ' ', s)).strip().lower()
def itext(it): return norm(DESC.sub(' ', it['slots']))
def atext(p): return norm(' '.join(t for b in p['blocks'] if not b.get('disabled') for t in block_texts(b)))
def sigsim(a, f):
    if not a and not f: return 1.0
    if len(a) == len(f): return sum(1 for x, y in zip(a, f) if x == y or 'x' in (x, y)) / len(a)
    return 0.5 * (1 - abs(len(a) - len(f)) / max(len(a), len(f))) + 0.5 * difflib.SequenceMatcher(None, a, f).ratio()
def sim(p, it):
    a, b = atext(p), itext(it)
    ts = 1.0 if not a and not b else difflib.SequenceMatcher(None, a, b).ratio()
    return 0.5 * sigsim(asig(p), FS.get(it['name'], '')) + 0.5 * ts
def group_of_admin(k):
    k = k.split('/'); return {'hdr':('header',''),'ftr':('footer',''),'title':('title','')}.get(k[0]) or (k[2], k[1])
def group_of_name(n):
    m = re.match(r'(header|footer|title)-(\d+)$', n)
    return (m.group(1), '') if m else tuple(n.rsplit('-', 2)[:2])
def align(A, B, gap=0.35):
    n, m = len(A), len(B); S = [[0.0]*(m+1) for _ in range(n+1)]; T = [[None]*(m+1) for _ in range(n+1)]
    for i in range(1, n+1): S[i][0] = -gap*i; T[i][0] = 'u'
    for j in range(1, m+1): S[0][j] = -gap*j; T[0][j] = 'l'
    sc = [[sim(A[i], B[j]) for j in range(m)] for i in range(n)]
    for i in range(1, n+1):
        for j in range(1, m+1):
            opts = [(S[i-1][j-1] + sc[i-1][j-1], 'd'), (S[i-1][j] - gap, 'u'), (S[i][j-1] - gap, 'l')]
            S[i][j], T[i][j] = max(opts)
    i, j, pairs = n, m, []
    while i > 0 or j > 0:
        t = T[i][j]
        if t == 'd': pairs.append((A[i-1], B[j-1], sc[i-1][j-1])); i -= 1; j -= 1
        elif t == 'u': pairs.append((A[i-1], None, 0)); i -= 1
        else: pairs.append((None, B[j-1], 0)); j -= 1
    return pairs[::-1]
def build():
    gA, gB = defaultdict(list), defaultdict(list)
    for p in P: gA[group_of_admin(p['preset_key'])].append(p)
    for it in I: gB[group_of_name(it['name'])].append(it)
    M = []
    for g in sorted(set(gA) | set(gB)):
        A = sorted(gA[g], key=lambda p: p['preset_key']); B = sorted(gB[g], key=lambda it: it['name'])
        M += [(g, a, b, s) for a, b, s in align(A, B)]
    return M
if __name__ == '__main__':
    M = build()
    diff = [(g, a['preset_key'] if a else None, b['name'] if b else None, round(s, 2)) for g, a, b, s in M
            if not a or not b or admin_to_name(a['preset_key']) != b['name']]
    low = [(a['preset_key'], b['name'], round(s, 2), asig(a), FS.get(b['name'])) for g, a, b, s in M if a and b and s < 0.6]
    print('pairs', sum(1 for _, a, b, _ in M if a and b), 'admin-only', sum(1 for _, a, b, _ in M if a and not b), 'figma-only', sum(1 for _, a, b, _ in M if b and not a))
    print('NAME-RULE DIFFS:'); [print(' ', d) for d in diff]
    print('LOW SCORE MATCHES (<0.6):'); [print(' ', l) for l in sorted(low, key=lambda x: x[2])]
