import os
import json, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
TAGS = ['일시·기간','운영시간','장소명','가격·요금','혜택·쿠폰','계좌·송금','메뉴·품목','스펙·제원 표','시간표·프로그램','절차·단계',
        '분류 2단','모집 요강','인물','이력·경력','실적·수치','후기·사례','FAQ','유의사항·규정','사진 모음','소식·아티클','채널·링크','영상']
def box(v):
    if v is None: return [0,0,0,0]
    if isinstance(v,(int,float)): return [float(v)]*4
    nums=[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', str(v))]
    if not nums: return [0,0,0,0]
    if len(nums)==1: return nums*4
    if len(nums)==2: return [nums[0],nums[1],nums[0],nums[1]]
    if len(nums)==3: return [nums[0],nums[1],nums[2],nums[1]]
    return nums[:4]
def rgba(c):
    if not c or not isinstance(c,str): return None
    c=c.strip().lower()
    if c in ('none','transparent',''): return None
    m=re.match(r'#([0-9a-f]{6})([0-9a-f]{2})?$',c)
    if m:
        h=m.group(1); a=int(m.group(2),16)/255 if m.group(2) else 1.0
        return (int(h[0:2],16),int(h[2:4],16),int(h[4:6],16),a)
    m=re.match(r'rgba?\(([^)]*)\)',c)
    if m:
        p=[float(x) for x in re.findall(r'[\d.]+',m.group(1))]
        return (p[0],p[1],p[2],p[3] if len(p)>3 else 1.0)
    return None
def is_page_bg(c): return c and abs(c[0]-250)<6 and abs(c[1]-250)<6 and abs(c[2]-250)<6
def bg_kind(b):
    s=b.get('style') or {}
    c=rgba(s.get('background'))
    if not c or is_page_bg(c) or c[3]<0.02: return None
    return 'solid' if c[3]>=0.5 else 'tint'
def side_margin(b):
    m=box((b.get('style') or {}).get('margin')); return m[1]+m[3]
def side_pad(b):
    p=box((b.get('style') or {}).get('padding')); return p[1]+p[3]
def has_bgimg(b): return bool((b.get('backgroundImage') or {}).get('enabled'))
def img_count(b):
    t=b['type']
    if t=='image': return 1
    if t=='gallery': return len((b.get('gallery') or {}).get('images',[]) or [])
    if t=='multiCard': return sum(1 for i in (b['multiCard'].get('items') or []) if i.get('type')=='image')
    if t in('profile','youtube','location'): return 1
    if t=='product': return len((b.get('product') or {}).get('items',[]) or [])
    return 1 if has_bgimg(b) else 0
def fullbleed_img(b):
    if b['type'] in ('image','gallery') and side_margin(b)==0 and side_pad(b)==0: return True
    return has_bgimg(b) and side_margin(b)==0
def texts_of(bl): return [t for b in bl for t in block_texts(b)]

def analyze(p, slots=''):
    bl=[b for b in p['blocks'] if not b.get('disabled')]
    key=p['preset_key']; kind=('header' if key.startswith('hdr/') else 'footer' if key.startswith('ftr/') else 'title' if key.startswith('title/') else key.split('/')[2])
    T=texts_of(bl); J=' ⏎ '.join(T)+' ⏎ '+slots
    types=[b['type'] for b in bl]
    tags=[]; why={}
    def add(t,r):
        if t not in tags: tags.append(t); why[t]=r
    nimg=sum(img_count(b) for b in bl)
    date_single=re.findall(r'YYYY\.? ?MM\.? ?DD|MM\.DD|20\d\d\.\d\d\.\d\d|일시|날짜|일정 정보|기간', J)
    hhmm=len(re.findall(r'hh:mm',J))
    years=re.findall(r'YYYY(?:\.MM|\.DD)?\s*[–-]\s*YYYY|YYYY(?:\.(?:MM|DD))?(?=\s*(?:⏎|\|)\s*이력)|이력', J)
    if kind not in ('header','footer','title'):
        # 시간표 / 이력 / 소식 / 후기 / 일시
        if hhmm>=2 and re.search(r'프로그램|내용|세션',J): add('시간표·프로그램','행마다 hh:mm')
        if re.search(r'이력|YYYY\.MM\s*[–-]\s*YYYY',J): add('이력·경력','연도+이력')
        if re.search(r'★',J) or re.search(r'리뷰|작성자',J): add('후기·사례','별점·작성자')
        if re.search(r'소식',J): add('소식·아티클','소식 제목+날짜')
        if '시간표·프로그램' not in tags and '이력·경력' not in tags and '후기·사례' not in tags and '소식·아티클' not in tags:
            if date_single or hhmm==1: add('일시·기간','날짜·시간 칸')
        if re.search(r'장소명|장소',J): add('장소명','장소 칸')
        # 가격 / 혜택 / 계좌
        if re.search(r'\d+,?0+원|가격|₩|정상가|원산지|00,000', J): add('가격·요금','가격 칸')
        if re.search(r'쿠폰|% ?OFF|할인|증정|무료|혜택',J): add('혜택·쿠폰','쿠폰·할인·혜택')
        if re.search(r'계좌|예금주|은행',J): add('계좌·송금','계좌')
        # 품목 / 스펙 / 표
        rows_buy=sum(1 for b in bl if b['type']=='multiCard' and any(i.get('type')=='button' for i in b['multiCard'].get('items') or []))
        if re.search(r'상품명|구성품|품목',J) and kind!='purchase' or (kind=='purchase' and not re.search(r'구매하기',J) and re.search(r'상품명.*상품명',J,re.S)):
            add('메뉴·품목','이름(+가격) 진열 행')
        if re.search(r'단위 등의 설명|수치단위|용량|소재|사이즈|cm|kg',J) or ('value' in J and re.search(r'\bA\b',J)): add('스펙·제원 표','라벨+값+단위')
        if re.search(r'00단위|00분|0{2,}%|\b00\b(?!:)',J) and kind in('key_info','materials'): add('실적·수치','큰 숫자+단위')
        # 절차 / 분류 2단 / FAQ
        nums=re.findall(r'(?:^|⏎ |\| )(?:0[1-9]|STEP|❶|❷|❸|❹|①|②|③)',' ⏎ '.join(T))
        if len(nums)>=2 and hhmm==0 and '구성품' not in J: add('절차·단계','번호 매긴 단계')
        if re.search(r'질문',J) and re.search(r'답변',J): add('FAQ','질문·답변 쌍')
        lab=[t for t in T if t.lower()=='label' or t=='LABEL']
        # 사진 모음
        gal=[b for b in bl if b['type']=='gallery']
        if gal or nimg>=2 and kind not in('contact',):
            imgs_with_text=sum(1 for b in bl if b['type']=='multiCard' and any(i.get('type')=='image' for i in b['multiCard'].get('items') or []) and any(i.get('type')=='text' for i in b['multiCard'].get('items') or []))
            if gal or (nimg>=2 and imgs_with_text==0): add('사진 모음','이미지 2장+')
        # 인물 (반복)
        if sum(1 for b in bl if b['type']=='profile')>=2 or len(re.findall(r'프로필 이미지',slots))>=2: add('인물','인물 사진+이름 반복')
        # 채널·링크 (문의 서랍 밖)
        if kind!='contact':
            if any(b['type']=='menu' for b in bl): add('채널·링크','메뉴 카드(이동 링크)')
            nbtn=sum(1 for b in bl if b['type']=='button')+sum(1 for b in bl if b['type']=='multiCard' for i in b['multiCard'].get('items') or [] if i.get('type')=='button')
            if nbtn>=2 and kind not in ('purchase','reservation','promo'): add('채널·링크','버튼 링크 반복')
            if re.search(r'→',J) and kind=='list': add('채널·링크','→ 링크 행')
        if any(b['type']=='youtube' for b in bl): add('영상','유튜브 카드')
        if re.search(r'유의|취소|환불|배송|교환|규정|준비물',J): add('유의사항·규정','규정 키워드')
    else:
        if any(b['type']=='sns' for b in bl) or re.search(r'@sns_id|SNS',J): add('채널·링크','SNS')
    # weight
    wide=[b for b in bl if side_margin(b)<40]
    solid_wide=[b for b in bl if bg_kind(b)=='solid' and side_margin(b)==0 and b['type'] not in('button',)]
    tint_wide=[b for b in bl if bg_kind(b)=='tint' and side_margin(b)==0]
    tint_any=[b for b in bl if bg_kind(b) in('tint','solid')]
    content=[b for b in bl if b['type']!='divider']
    fb=[b for b in bl if fullbleed_img(b)]
    if solid_wide or fb or (content and len(tint_wide)/len(content)>=0.5):
        w='heavy'; wr=('색 밴드' if solid_wide else '풀블리드 이미지' if fb else '대면적 틴트')
    elif nimg>=1 or tint_any:
        w='medium'; wr=('이미지' if nimg else '틴트 카드')
    else:
        w='light'; wr='텍스트 위주'
    # items
    items=None
    sw=[b for b in bl if b['type']=='gallery' and (b['gallery'].get('type')=='swipe')]
    if sw: items='4~15'
    elif kind=='key_info':
        cols=[b for b in bl if b['type']=='multiCard' and len(b['multiCard'].get('items') or [])>=2 and len({i.get('type') for i in b['multiCard']['items']})==1 and len(set(lex_texts(b['multiCard']['items'][0].get('content'))) & set(lex_texts(b['multiCard']['items'][1].get('content'))))>0]
        items='2~4' if cols else '1~4'
    elif any(b['type']=='gallery' for b in bl): items='1~15'
    # conditions
    cond=[]
    hero_fb = kind=='hero' and (any(fullbleed_img(b) for b in bl))
    if hero_fb: cond.append('유저가 준 메인 이미지(포스터·대표 사진)가 있을 때만 — 없으면 이미지 없는 히어로')
    if any(b['type']=='product' for b in bl): cond.append('상품 구매 링크(URL)가 있을 때만 — 상품 카드는 링크로 상품을 불러온다')
    if any(b['type']=='menu' for b in bl): cond.append('페이지 안 이동 메뉴가 필요할 때 — 메뉴 카드는 페이지 맨 위에 고정된다')
    if sw: cond.append('넘길 이미지가 4장 이상일 때')
    if any(b['type']=='sns' for b in bl): cond.append('SNS 계정이 2개 이상일 때')
    return dict(key=key, kind=kind, tags=tags, why=why, weight=w, wr=wr, items=items, cond=cond, nimg=nimg, texts=T)
