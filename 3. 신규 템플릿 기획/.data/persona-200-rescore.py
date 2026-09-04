# -*- coding: utf-8 -*-
import json, io
SKILL={"상":50,"중":88,"하":62}; MAT={"풍부":62,"보통":82,"빈약":56}
CLAR={"명확":122,"보통":63,"모호":15}
CT={("상","풍부"):34,("상","보통"):16,("상","빈약"):0,
    ("중","풍부"):25,("중","보통"):56,("중","빈약"):7,
    ("하","풍부"):3, ("하","보통"):10,("하","빈약"):49}
qr={"상":2,"중":1,"하":0}; mr={"풍부":2,"보통":1,"빈약":0}
# 목적 배정: 상+풍부 셀은 34명 중 30명만 「명확」 (기록된 교차표 준수)
FORCE={("상","풍부"):{"명확":30,"보통":4}}
people=[]; left=dict(CLAR)
cells=sorted(CT.items(), key=lambda kv:-(qr[kv[0][0]]+mr[kv[0][1]]))
for key,n in cells:
    if key in FORCE:
        for c,k in FORCE[key].items():
            for _ in range(k): left[c]-=1; people.append({"skill":key[0],"mat":key[1],"clar":c})
        continue
    for _ in range(n):
        for c in ("명확","보통","모호"):
            if left[c]>0: left[c]-=1; people.append({"skill":key[0],"mat":key[1],"clar":c}); break
assert len(people)==200 and all(v==0 for v in left.values()), left
# 업종군
cr={"명확":2,"보통":1,"모호":0}
idx=sorted(range(200), key=lambda i:(-(qr[people[i]["skill"]]*2+mr[people[i]["mat"]]*2+cr[people[i]["clar"]]), i))
seq=[]
while len(seq)<200:
    for s in ["E","C","A","B","D"]:
        if seq.count(s)<40: seq.append(s)
for rank,i in enumerate(idx): people[i]["sect"]=seq[rank]
# 결정적 지터 (개인 요인) — 셀 안에서 순환
JIT=[-4.1,-2.4,-1.0,0.3,1.2,2.6,4.0,-3.2,1.9,-0.5]
from collections import defaultdict
cnt=defaultdict(int)
for p in people:
    k=(p["skill"],p["mat"],p["clar"]); p["j"]=JIT[cnt[k]%len(JIT)]; cnt[k]+=1

def axes(p):
    D1={"명확":3.95,"보통":3.45,"모호":2.45}[p["clar"]]+{"상":.25,"중":0,"하":-.40}[p["skill"]]
    D2=3.30+{"A":-.14,"B":-.50,"C":.02,"D":-.55,"E":.10}[p["sect"]]+{"풍부":.28,"보통":0,"빈약":-.20}[p["mat"]]
    D3={"풍부":4.10,"보통":3.25,"빈약":2.35}[p["mat"]]+{"명확":.18,"보통":0,"모호":-.28}[p["clar"]]
    D4=3.62+{"A":.20,"B":-.15,"C":.10,"D":-1.20,"E":.35}[p["sect"]]+{"풍부":.35,"보통":0,"빈약":-.48}[p["mat"]]
    D5={"상":4.05,"중":3.35,"하":2.55}[p["skill"]]+{"풍부":0,"보통":-.10,"빈약":-.30}[p["mat"]]+{"명확":.10,"보통":0,"모호":-.32}[p["clar"]]
    return [D1,D2,D3,D4,D5]

def score(p, ax):
    ax=[max(0,min(5,x)) for x in ax]
    return ax, max(3,min(25, round(sum(ax)+p["j"])))

for p in people:
    p["as"],p["as_t"]=score(p, axes(p))

def report(key,label):
    t=[p[key] for p in people]; m=sum(t)/200
    print("\n[%s] 평균 %.2f · 중앙 %d · 20↑ %d · 13↓ %d"%(label,m,sorted(t)[100],
        sum(1 for x in t if x>=20), sum(1 for x in t if x<=13)))
    for lab,f,rec in [("업종군",lambda p:p["sect"],["E","C","A","B","D"]),
                      ("숙련도",lambda p:p["skill"],["상","중","하"]),
                      ("자료",  lambda p:p["mat"],["풍부","보통","빈약"]),
                      ("목적",  lambda p:p["clar"],["명확","보통","모호"])]:
        out=[]
        for g in rec:
            sub=[p[key] for p in people if f(p)==g]
            out.append("%s %.2f/%d↑%d"%(g,sum(sub)/len(sub),len(sub),sum(1 for x in sub if x>=20)))
        print("   %-4s"%lab," · ".join(out))
report("as_t","AS-IS")
print("\n기록값: 평균16.45 중앙17 20↑37 13↓49 | 업종 E17.20 C17.00 A16.30 B16.18 D15.60 | 숙련 상19.00 중17.33 하13.16 | 자료 풍부18.92 보통16.94 빈약13.02 | 목적 명확18.04 보통14.60 모호11.33")
json.dump(people, io.open("/tmp/cohort.json","w",encoding="utf-8"), ensure_ascii=False)

sub=[p["as_t"] for p in people if p["skill"]=="하" and p["mat"]=="빈약"]
print("\n하+빈약 n=%d 평균 %.2f 20↑%d (기록 n49 12.57 0)"%(len(sub),sum(sub)/len(sub),sum(1 for x in sub if x>=20)))
sub=[p["as_t"] for p in people if p["skill"]=="상" and p["mat"]=="풍부" and p["clar"]=="명확"]
print("상+풍부+명확 n=%d 평균 %.2f 20↑%d (기록 n30 20.13 19)"%(len(sub),sum(sub)/len(sub),sum(1 for x in sub if x>=20)))
lo=sum(1 for p in people if (p["skill"]=="하" or p["mat"]=="빈약"))
lo20=sum(1 for p in people if (p["skill"]=="하" or p["mat"]=="빈약") and p["as_t"]>=20)
print("숙련하 또는 자료빈약 n=%d · 그중 20↑ %d (기록 n93 0)"%(lo,lo20))
exec(open('3. 신규 템플릿 기획/.data/persona-200-rescore.py',encoding='utf-8').read().split('report("as_t"')[0])

AX=["D1 분류적중","D2 레시피","D3 자료충족","D4 디자인","D5 완주"]

def apply_gain(p, conf):
    d=list(p["as"])
    m,s,c,se=p["mat"],p["skill"],p["clar"],p["sect"]
    # G1 「함께 담을 것」 칩 — AI가 자료 근거로 미리 켬 (근거 없으면 안 켜짐)
    d[0]+= {"풍부":1.05,"보통":0.75,"빈약":0.25}[m]
    # G2 ②-B 타겟 확인 (통보형)
    d[0]+= {"풍부":0.45,"보통":0.40,"빈약":0.25}[m]
    d[3]+= 0.10 if se=="D" else 0.30
    # G3 빈 자리 처리 규칙 + 「이건 없어요」 + 미리 채워두고 확인
    d[2]+= {"빈약":1.30,"보통":0.80,"풍부":0.30}[m]
    d[2]= min(d[2], 4.40)          # 사실정보(가격·마감·정원)는 여전히 AI가 못 채움 → 만점 불가
    # G4 ④ 통보형 + ③ 답하는 방식 5가지
    d[4]+= {"하":1.45,"중":0.70,"상":0.20}[s] + (0.20 if c=="모호" else 0)
    # G5 D2 = 0 (주문서·표·검색·파일·알림 카드 미착수)
    if conf=="검토중":
        d[4]+=0.50; d[3]+=0.40           # D안(3안 탭 + 즉시 반영)
        d[1]+=0.20                        # 원/멀티 4관문
        d[3]+= 0.25 if m=="빈약" else 0.10   # 미리보기 스타일 규칙
    d=[max(0,min(5,x)) for x in d]
    return d, max(3,min(25, round(sum(d)+p["j"])))

for p in people:
    p["c1"],p["c1_t"]=apply_gain(p,"확정")
    p["c2"],p["c2_t"]=apply_gain(p,"검토중")

def block(key,label):
    t=[p[key] for p in people]; m=sum(t)/200
    print("\n■ %s — 평균 %.2f · 중앙 %d · 20↑ %d(%.0f%%) · 13↓ %d(%.0f%%)"%(
        label,m,sorted(t)[100],sum(1 for x in t if x>=20),sum(1 for x in t if x>=20)/2,
        sum(1 for x in t if x<=13),sum(1 for x in t if x<=13)/2))
    for lab,f,gs in [("업종군",lambda p:p["sect"],["A","B","C","D","E"]),
                     ("숙련도",lambda p:p["skill"],["상","중","하"]),
                     ("자료",  lambda p:p["mat"],["풍부","보통","빈약"]),
                     ("목적",  lambda p:p["clar"],["명확","보통","모호"])]:
        out=[]
        for g in gs:
            sub=[p[key] for p in people if f(p)==g]
            out.append("%s %.2f(20↑%d)"%(g,sum(sub)/len(sub),sum(1 for x in sub if x>=20)))
        print("    %-4s"%lab," · ".join(out))

for k,l in [("as_t","AS-IS (rev.1 기준)"),("c1_t","TO-BE ① 확정분만"),("c2_t","TO-BE ② 검토중까지 채택")]:
    block(k,l)

print("\n\n■ 축별 평균 (0~5)")
print("    %-12s %6s %6s %6s   %s"%("축","AS-IS","확정","검토중","증감(확정)"))
for i,a in enumerate(AX):
    v0=sum(p["as"][i] for p in people)/200; v1=sum(p["c1"][i] for p in people)/200; v2=sum(p["c2"][i] for p in people)/200
    print("    %-12s %6.2f %6.2f %6.2f   %+.2f"%(a,v0,v1,v2,v1-v0))

print("\n\n■ 취약군 3개 — 이번 개정이 정확히 겨냥한 사람들")
for lab,f in [("숙련도 하 (62명)",lambda p:p["skill"]=="하"),
              ("자료 빈약 (56명)",lambda p:p["mat"]=="빈약"),
              ("하＋빈약 (49명)",lambda p:p["skill"]=="하" and p["mat"]=="빈약"),
              ("하 또는 빈약 (69명)",lambda p:p["skill"]=="하" or p["mat"]=="빈약"),
              ("목적 모호 (15명)",lambda p:p["clar"]=="모호"),
              ("상＋풍부＋명확 (30명)",lambda p:p["skill"]=="상" and p["mat"]=="풍부" and p["clar"]=="명확")]:
    s=[p for p in people if f(p)]
    a=sum(p["as_t"] for p in s)/len(s); b=sum(p["c1_t"] for p in s)/len(s); c=sum(p["c2_t"] for p in s)/len(s)
    print("    %-22s %5.2f → %5.2f (%+.2f) → %5.2f (%+.2f) · 20↑ %d→%d→%d"%(
        lab,a,b,b-a,c,c-a,sum(1 for p in s if p["as_t"]>=20),sum(1 for p in s if p["c1_t"]>=20),sum(1 for p in s if p["c2_t"]>=20)))

print("\n\n■ 분포 이동")
def hist(key):
    import collections
    b=collections.Counter()
    for p in people:
        t=p[key]
        b[" 5~ 9" if t<10 else "10~14" if t<15 else "15~19" if t<20 else "20~24" if t<25 else "   25"]+=1
    return b
h0,h1,h2=hist("as_t"),hist("c1_t"),hist("c2_t")
print("    %-8s %6s %6s %6s"%("구간","AS-IS","확정","검토중"))
for k in [" 5~ 9","10~14","15~19","20~24","   25"]:
    print("    %-8s %6d %6d %6d"%(k,h0[k],h1[k],h2[k]))

json.dump(people, io.open("/Users/leesunho/Documents/GitHub/design/cdbd-templates/3. 신규 템플릿 기획/.data/persona-200-cohort.json","w",encoding="utf-8"), ensure_ascii=False, indent=0)
print("\n코호트 저장: 3. 신규 템플릿 기획/.data/persona-200-cohort.json")

# ── 보수 시나리오: 개정 효과가 설계 의도의 55%만 발휘될 때 ──────────
def conservative(p):
    d=list(p["as"]); f=0.55
    m,s,c,se=p["mat"],p["skill"],p["clar"],p["sect"]
    d[0]+= f*({"풍부":1.05,"보통":0.75,"빈약":0.25}[m] + {"풍부":0.45,"보통":0.40,"빈약":0.25}[m])
    d[3]+= f*(0.10 if se=="D" else 0.30)
    d[2]= min(d[2]+f*{"빈약":1.30,"보통":0.80,"풍부":0.30}[m], 4.40)
    d[4]+= f*({"하":1.45,"중":0.70,"상":0.20}[s] + (0.20 if c=="모호" else 0))
    d=[max(0,min(5,x)) for x in d]
    return max(3,min(25, round(sum(d)+p["j"])))
for p in people: p["cons"]=conservative(p)
t=[p["cons"] for p in people]
print("\n\n■ 보수 시나리오 (효과 55퍼센트만 발휘) — 평균 %.2f · 20↑ %d · 13↓ %d"%(sum(t)/200,sum(1 for x in t if x>=20),sum(1 for x in t if x<=13)))
for lab,f in [("숙련도 하",lambda p:p["skill"]=="하"),("자료 빈약",lambda p:p["mat"]=="빈약"),("하＋빈약",lambda p:p["skill"]=="하" and p["mat"]=="빈약")]:
    s=[p for p in people if f(p)]
    print("    %-10s %5.2f → %5.2f · 20↑ %d→%d"%(lab,sum(p["as_t"] for p in s)/len(s),sum(p["cons"] for p in s)/len(s),
        sum(1 for p in s if p["as_t"]>=20),sum(1 for p in s if p["cons"]>=20)))

print("\n\n■ 개정 후 가장 낮은 축 = 다음 병목")
for i,a in enumerate(AX):
    v=sum(p["c1"][i] for p in people)/200
    print("    %-12s %.2f  %s"%(a,v,"◀ 병목" if a.startswith("D2") else ""))
