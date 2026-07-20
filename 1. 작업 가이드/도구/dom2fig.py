import re, json
from html.parser import HTMLParser

def expand(style):
    d={}
    for p in (style or '').split(';'):
        if ':' not in p: continue
        k,v=p.split(':',1); k=k.strip().lower(); v=v.strip()
        if k=='font':
            # ⚠️ 'font: italic 400 26px/1 ...' 처럼 style/variant 키워드가 앞설 수 있다.
            #    예전 정규식은 weight로 시작한다고 가정해 매치 실패 → 크기·폰트가 통째로 버려졌다.
            #    기울임은 CdBd에 없는 옵션이라(CLAUDE.md 폰트 원칙 11) 읽고 나서 버린다 = 정체로 렌더.
            m=re.match(r"(?:(?:italic|oblique|small-caps|normal)\s+)*"
                       r"(\d+)\s+([\d.]+)px(?:/([\d.]+))?\s+(.+)", v)
            if m:
                d['font-weight']=m.group(1); d['font-size']=float(m.group(2))
                if m.group(3): d['line-height']=float(m.group(3))
                # ⚠️ 예전엔 'serif'/'sans' 2값으로 뭉갰다 → 나눔명조 등이 전부 Pretendard로 떨어짐.
                #    실제 패밀리 문자열을 그대로 보존하고, 매핑은 렌더러(famOf)가 한다.
                d['font-family']=m.group(4).strip()
            continue
        d[k]=v
    return d

def px4(v):
    if not v: return [0,0,0,0]
    parts=[p for p in v.replace('px','').split() if p]
    try: n=[float(x) for x in parts]
    except: return [0,0,0,0]
    if len(n)==1: return [n[0]]*4
    if len(n)==2: return [n[0],n[1],n[0],n[1]]
    if len(n)==3: return [n[0],n[1],n[2],n[1]]
    return n[:4]

class Tree(HTMLParser):
    def __init__(s):
        super().__init__(); s.root={'tag':'root','style':{},'children':[],'text':None}; s.stack=[s.root]
    VOID={'br','img','input','hr','source','image-slot','meta','link'}
    def handle_starttag(s,tag,attrs):
        a=dict(attrs); st=expand(a.get('style',''))
        if 'ph' in (a.get('class','') or '').split(): st['_ph']=True
        n={'tag':tag,'style':st,'children':[],'text':None}
        s.stack[-1]['children'].append(n)
        if tag not in s.VOID: s.stack.append(n)
    def handle_startendtag(s,tag,attrs): pass
    def handle_endtag(s,tag):
        if len(s.stack)>1: s.stack.pop()
    def handle_data(s,data):
        t=data.strip()
        if t: s.stack[-1]['children'].append({'tag':'#text','style':{},'children':[],'text':t})

def layout(n, W):
    """compute width/height top-down"""
    st=n['style']
    n['w']=W
    pad=px4(st.get('padding'))
    inner=W-pad[1]-pad[3]
    flex = st.get('display')=='flex'
    grid = st.get('display')=='grid'
    row = flex and st.get('flex-direction')!='column'
    kids=[c for c in n['children'] if c['tag']!='#text']
    if grid and kids:
        gtc=st.get('grid-template-columns','1fr 1fr'); ncol=max(len(gtc.split()),1)
        gap=float(re.sub(r'[^\d.]','',st.get('gap','0')) or 0)
        each=(inner-gap*(ncol-1))/ncol
        for c in kids: layout(c, each)
    elif row and kids:
        gap=float(re.sub(r'[^\d.]','',st.get('gap','0')) or 0)
        fixed=0; flexn=0
        for c in kids:
            cw=c['style'].get('width')
            if cw and cw.endswith('px'): fixed+=float(cw[:-2])
            else: flexn+=1
        avail=inner-gap*(len(kids)-1)-fixed
        each=avail/flexn if flexn else 0
        for c in kids:
            cw=c['style'].get('width')
            layout(c, float(cw[:-2]) if (cw and cw.endswith('px')) else each)
    else:
        for c in kids: layout(c, inner)
    # explicit height
    hh=st.get('height')
    if hh and hh.endswith('px'):
        try: n['h']=float(hh[:-2])
        except: pass
    # aspect-ratio height
    ar=st.get('aspect-ratio')
    if ar:
        try:
            if '/' in ar:
                a,b=ar.split('/'); n['h']=n['w']*float(b)/float(a)
            else:
                n['h']=n['w']/float(ar.strip())
        except: pass
    return n

def build(fragment, W=390):
    t=Tree(); t.feed(fragment)
    root=t.root
    layout(root, W)
    return root
