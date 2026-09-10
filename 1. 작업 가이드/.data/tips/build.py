# 1-14 재조립 스크립트 — g1~g6 + 1-① 표를 합쳐 정본 노트를 생성
import io,re,os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..'))
head=io.open('.data/tips/_HEAD.md',encoding='utf-8').read()
parts=[head]
for f in ['.data/tips/g%d.md'%i for i in range(1,7)]:
    s=io.open(f,encoding='utf-8').read()
    s=re.sub(r'\A(?:(?!^####).)*?(?=^####)','',s,flags=re.S|re.M)
    parts.append(s.strip()+'\n')
out='\n---\n\n'.join(parts)
heads={'2-①':'## 2. 프로필·명함','3-①':'## 3. 소개·홈페이지','4-①':'## 4. 상품·홍보','5-①':'## 5. 신청·문의','6-①':'## 6. 소식·자료'}
for k,v in heads.items():
    out=re.sub(r'^(#### '+re.escape(k)+r'\b)', v+'\n\n'+r'\1', out, count=1, flags=re.M)
io.open('1-14. 입력 단계 안내 문구.md','w',encoding='utf-8').write(out)
print('built')
