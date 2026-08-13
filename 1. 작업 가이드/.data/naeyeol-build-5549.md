# 나열 프리셋 빌드 — editor 5549 (작업 진행 상태)

> 정본 절차 = `.data/cdbd-preset-build-recipe.md` (5541 히어로 빌드 검증본, 기법 동일).
> 이 파일 = 5549 나열 전용 매니페스트 + 진행 로그. 브라우저 = gstack `$B` 공유 세션.

## 환경 / 로그인 복구
- 에디터: https://cdbd-client-git-ai-makevu-s-team.vercel.app/editor/5549
- 어드민(확인): https://cdbd-client-git-ai-makevu-s-team.vercel.app/admin/ai/presets
- ⚠️ **`$B viewport` 절대 호출 금지** — context recreate로 쿠키·탭 날아가 로그아웃됨(이번 세션 사고).
- 로그아웃 시 복구: goto `/login` → 인풋 `#email`/`#password` 이미 id 있음 → `$B fill` → **정확히 `로그인하기` 텍스트 버튼** click(‘Google 계정으로 로그인하기’ 아님!). 계정=account@emka.group, 비번=vault `.env` CDBD_PASSWORD.
- 드라이버: `$B eval .claude/skills/cdbd-card-automation/card-driver.js` → window.__cdbd.
- Figma 원본 페이지 = fileKey `24O01lprp5i2ufl7CbZXXx`, page `34:23`. 노드 dump는 recipe §2.

## 페이지 구조 (간지 = 스타일 구분 페이지)
- p1 = 간지「나열 미니멀」 · p6 = 간지「나열 에디토리얼」 · p7 = 간지「나열 볼드」
- p2~5 = 미니멀 프리셋 4장 (이미 완성).
- 새 페이지는 **맨끝 append** → 빌드 후 **해당 간지 아래로 reorder**.

## 등록 키 규칙 (purpose slug = list)
- 미니멀 전용 → `sec/minimal/list/NN` (01~04 사용됨 → 05부터)
- 에디토리얼 전용 → `sec/editorial/list/NN`
- 볼드 전용 → `sec/bold/list/NN`
- 공통(멀티태그) → `sec/mixed/list/NN` + 저장모달에서 해당 스타일 토글 여러 개 ON. 배치=첫 스타일 간지 아래.

## 완성(DONE) — 다시 만들지 말 것
- 5408:274 (미볼, 3버튼) = page2
- 5408:90 (미에볼, 항목·세부 3텍스트) = page4
- 5408:212 (미에, 항목⇥세부 3텍스트) = page5
- page3 = plain 항목x3 (레거시, 매칭 노드 없음)

## 빌드 대기 — 미니멀 간지 아래 (배치: p5 뒤 ~ p6 앞)
| Figma | cards | 내용 | 태그 | 키 |
|---|---|---|---|---|
| 5408:317 | 17 | 갤러리+버튼 리치 리스트 | minimal | sec/minimal/list/05 |
| 5408:372 | 7  | 버튼 리스트+구분선 | minimal | sec/minimal/list/06 |
| 5408:389 | 3  | ❶❷❸ 원두(2줄 텍스트) | minimal | sec/minimal/list/07 |
| 5408:219 | 18 | 메인+서브갤러리+2단 | minimal+editorial | sec/mixed/list/NN |
| 5408:97  | 4  | 메뉴(항목→) | all3 | sec/mixed/list/NN |
| 5408:114 | 13 | 리뷰(★+내용+날짜) 구분선 | all3 | sec/mixed/list/NN |
| 5408:144 | 3  | 리뷰 3텍스트 | all3 | sec/mixed/list/NN |
| 5408:154 | 14 | 2단 카드 반복 | all3 | sec/mixed/list/NN |
| 5408:191 | 4  | 💡 항목+세부 | all3 | sec/mixed/list/NN |

## 빌드 대기 — 에디토리얼 간지 아래 (p6 뒤 ~ p7 앞)
- 에디토리얼 전용(10): 5408:408, 418, 428, 438, 448, 461(17c), 518(9c), 539(8c), 563(8c), 582(8c) → sec/editorial/list/NN
- 에볼(2): 5408:286(4c), 302(3c) → sec/mixed/list/NN (에+볼 토글)

## 빌드 대기 — 볼드 간지 아래 (p7 뒤)
- 볼드 전용(9): 5408:603, 613, 623(6c), 642(4c), 657(2c), 664(18c), 729(16c frag D②로컬매거), 776(3c), 786(3c) → sec/bold/list/NN

## 진행 로그
- (여기 각 프리셋 완료 시 키 기록)
