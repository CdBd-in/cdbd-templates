import os
import json, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from tagger import box, rgba, is_page_bg, bg_kind, side_margin, side_pad, has_bgimg, img_count, fullbleed_img
def items_of(b): return (b.get('multiCard') or {}).get('items') or []
def paras(b): return lex_texts(b.get('content'))
def analyze(p, slots='', figname=''):
    bl=[b for b in p['blocks'] if not b.get('disabled')]
    key=p['preset_key']
    kind=('header' if key.startswith('hdr/') else 'footer' if key.startswith('ftr/') else 'title' if key.startswith('title/') else key.split('/')[2])
    T=[t for b in bl for t in block_texts(b)]; J=' ⏎ '.join(T)
    tags=[]
    def add(t):
        if t not in tags: tags.append(t)
    hhmm=len(re.findall(r'hh:mm',J))
    btn_rows=sum(1 for b in bl if b['type']=='button' or (b['type']=='multiCard' and items_of(b) and all(i.get('type')=='button' for i in items_of(b))))
    nprod=len(re.findall(r'상품명',J))
    nbuy=len(re.findall(r'구매하기',J))
    photo_slots=[s for s in slots.split('|') if re.search(r'이미지|사진|비주얼',s) and not re.search(r'프로필|로고|아이콘|배경 이미지',s)]
    logo_slots=[s for s in slots.split('|') if '로고' in s]
    gal=[b for b in bl if b['type']=='gallery']
    if kind in ('header','footer','title'):
        sns=[b for b in bl if b['type']=='sns']
        if sns or '@sns_id' in J: add('채널·링크')
    else:
        if hhmm>=2: add('시간표·프로그램')
        if re.search(r'이력|YYYY\.MM\s*[–-]\s*YYYY',J): add('이력·경력')
        if re.search(r'★|리뷰|작성자',J): add('후기·사례')
        if '소식' in J: add('소식·아티클')
        if not set(tags)&{'시간표·프로그램','이력·경력','후기·사례','소식·아티클'}:
            if re.search(r'YYYY\.? ?MM\.? ?DD|MM\.DD|20\d\d\.\d\d\.\d\d|일시|날짜|일정 정보|기간',J) or hhmm==1: add('일시·기간')
        if re.search(r'장소',J): add('장소명')
        if re.search(r'\d+,?0{3}원|가격|₩|정상가|00,000',J): add('가격·요금')
        if re.search(r'쿠폰|% ?OFF|할인|증정|무료|혜택|사은품',J): add('혜택·쿠폰')
        if re.search(r'계좌|예금주|은행',J): add('계좌·송금')
        prodcards=any(b['type']=='product' for b in bl)
        if prodcards: add('가격·요금')
        if (nprod>=2 and nbuy==0 and btn_rows<nprod) or len(re.findall(r'구성품',J))>=2 or (prodcards and not re.search(r'구매하기',slots)):
            add('메뉴·품목')
        if re.search(r'단위 등의 설명|수치단위|용량|원산지|소재|사이즈|\bcm\b|\bkg\b',J) or (kind=='purchase' and len(re.findall(r'(?:^|⏎ )label(?: ⏎ |\n)',J,re.I))>=2) or ('value' in J and re.search(r'(?:^|⏎ )A(?: ⏎|$)',J)):
            add('스펙·제원 표')
        if (re.search(r'\d*0{2}\s*(?:단위|분|%)|00단위',J) and kind in('key_info','materials')) or (len(logo_slots)>=2 and kind=='materials') or (kind=='key_info' and re.search(r'(?:^|⏎ )00(?: ⏎|$)',J)):
            add('실적·수치')
        nums=re.findall(r'(?:^|⏎ )(?:0[1-9]|STEP|❶|❷|❸|❹|①|②|③)',J)
        if len(nums)>=2 and hhmm==0 and '구성품' not in J: add('절차·단계')
        # 분류 2단: 단독 label 텍스트가 2번+ 나오고 그 사이에 항목 행이 2개+
        groups=0
        for i,b in enumerate(bl):
            if b['type']=='text' and [x.strip().lower() for x in paras(b) if x.strip()]==['label']:
                run=0
                for c in bl[i+1:]:
                    if c['type']=='multiCard': run+=1
                    else: break
                if run>=2: groups+=1
        if groups>=2: add('분류 2단')
        if re.search(r'질문',J) and re.search(r'답변',J): add('FAQ')
        if re.search(r'유의|취소|환불|배송|교환|규정|준비물',J): add('유의사항·규정')
        img_only_rows=[b for b in bl if (b['type']=='multiCard' and len(items_of(b))>=2 and all(i.get('type')=='image' for i in items_of(b)))]
        if (gal or img_only_rows) and not prodcards and not (len(logo_slots)>=2 and not photo_slots):
            if kind!='hero' or gal: add('사진 모음')
        if sum(1 for b in bl if b['type']=='profile')>=2 or len(re.findall(r'프로필 이미지',slots))>=2 and kind!='list': add('인물')
        if kind!='contact':
            link_rows=0
            for i,b in enumerate(bl):
                if b['type']=='menu': link_rows+=2
                if b['type']=='button' and not (i>0 and bl[i-1]['type']=='text' and len([x for x in paras(bl[i-1]) if x.strip()])>=2): link_rows+=1
                if b['type']=='multiCard' and items_of(b) and all(it.get('type')=='button' for it in items_of(b)): link_rows+=len(items_of(b))
            if '→' in J and kind=='list': link_rows+=2
            if kind in('purchase','reservation','promo'): link_rows=0
            if link_rows>=2: add('채널·링크')
        if any(b['type']=='youtube' for b in bl): add('영상')
    # weight
    content=[b for b in bl if b['type']!='divider']
    solid_wide=[b for b in bl if bg_kind(b)=='solid' and side_margin(b)==0 and b['type']!='button']
    tint_wide=[b for b in bl if bg_kind(b)=='tint' and side_margin(b)==0]
    bgimgs=[b for b in bl if has_bgimg(b)]
    fb=[b for b in bl if fullbleed_img(b)]
    nimg=sum(img_count(b) for b in bl)
    if solid_wide or fb or (content and (len(tint_wide)/len(content)>=0.5 or len(bgimgs)/len(content)>=0.5)):
        w='heavy'
    elif nimg>=1 or any(bg_kind(b) for b in bl): w='medium'
    else: w='light'
    # items
    items=None
    def col_row(b):
        its=items_of(b)
        if b['type']!='multiCard' or len(its)<2: return False
        ty={i.get('type') for i in its}
        if len(ty)!=1: return False
        if ty=={'image'}: return True
        ts=[tuple(lex_texts(i.get('content'))) for i in its]
        return len(set(ts))==1 and ts[0]!=()
    crow=[b for b in bl if col_row(b)]
    sw=[b for b in gal if b['gallery'].get('type')=='swipe']
    if sw: items='4~15'
    elif kind=='key_info': items='2~4' if crow else '1~4'
    elif gal: items='1~15'
    elif crow and kind not in('header','footer','title') and len(crow)/max(1,len(content))>=0.5: items='2~4' if len(crow)==1 else '2~'
    # conditions
    cond=[]
    if kind=='hero' and (fb or bgimgs): cond.append('유저가 준 메인 이미지(포스터·대표 사진)가 있을 때만 — 없으면 이미지 없는 히어로')
    if any(b['type']=='product' for b in bl): cond.append('상품 구매 링크(URL)가 있을 때만 — 상품 카드는 링크로 상품을 불러온다')
    for b in bl:
        if b['type']=='menu' and b.get('fixedPosition')=='top': cond.append('페이지 안 이동 메뉴가 필요할 때 — 메뉴 카드는 페이지 맨 위에 고정된다'); break
    if sw: cond.append('넘길 이미지가 4장 이상일 때')
    for b in bl:
        if b['type']=='sns':
            n=sum(1 for c in (b.get('sns') or {}).get('channels',[]) if c.get('enabled'))
            cond.append('SNS 계정이 2개 이상일 때' if n>=2 else 'SNS 계정이 있을 때'); break
    else:
        if '@sns_id' in J: cond.append('SNS 계정이 있을 때')
    if kind=='header' and '메뉴 아이콘' in slots: cond.append('멀티페이지일 때만 — 메뉴 아이콘은 목차로 돌아가는 장치(원페이지 ❌)')
    if kind!='location' and any(b['type']=='location' for b in bl): cond.append('주소가 있을 때 — 지도 카드 포함')
    if figname=='list-bold-17': cond.append('타일마다 넣을 유저 이미지가 있을 때만 — 없으면 단색 버전(list-bold-18)')
    return dict(key=key, kind=kind, tags=tags, weight=w, items=items, cond=cond)
