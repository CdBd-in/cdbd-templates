---
title: AI 프리셋 어드민 ↔ 피그마 대조 (2026-09-08)
type: worklist
---

# AI 프리셋 어드민 업데이트 목록 (2026-09-08)

> 대조 대상: 어드민 `https://cdbd-client-git-ai-makevu-s-team.vercel.app/admin/ai/presets` (299개, 전부 게시됨) ↔ 피그마 「섹션 프리셋」 34:23 (355개).
> 확인된 규칙: **어드민 키 = 피그마 캔버스 순서(그룹 위→아래, 카드 왼→오른쪽)의 순번**. 오늘 정리한 피그마 번호와 같은 규칙이라, 차이는 전부 **신규 삽입 / 삭제로 인한 번호 밀림**에서만 발생한다.
> 검증: 살아있는 295개 중 288개가 블록 수까지 일치(나머지 7개는 아래 D 참조).

## 요약

| 구분 | 건수 |
|---|---|
| A. 신규 등록 필요 | **60** |
| B. 키(번호) 변경 필요 | **37** |
| C. 어드민에서 제거(피그마에 없음) | **4** |
| D. 내용이 달라진 듯 — 확인 필요 | 3 |
| 변경 없음 | 258 |

⚠️ **실행 순서 = C(제거) → B(번호 변경) → A(신규 등록)**. 번호가 밀리는 자리에 새 프리셋을 먼저 넣으면 키가 충돌한다.

---

## A. 신규 등록 60개

에디터에서 「프리셋 저장」으로 등록하고, 아래 키·목적·레이아웃 태그로 맞춘다.

| 새 키 | 피그마 이름 | 서랍 | 레이아웃 태그 | 높이 | 담는 칸 |
|---|---|---|---|---|---|
| `sec/bold/hero/09` | hero-bold-09 | 히어로-볼드 | 볼드 | 331 | 프로필 이미지 · 이름 · 한 줄 설명 |
| `sec/bold/hero/10` | hero-bold-10 | 히어로-볼드 | 볼드 | 350 | 메인 비주얼 · 페이지 제목 카피 혹은 설명 문구 · 버튼 텍스트 |
| `sec/bold/intro/04` | intro-bold-04 | 소개-볼드 | 볼드 | 105 | 소개 문구 |
| `sec/bold/list/13` | list-bold-13 | 나열-볼드 | 볼드 | 291 | YYYY · 이력 내용 · 구분선 · YYYY · 이력 내용 · 구분선 |
| `sec/bold/list/14` | list-bold-14 | 나열-볼드 | 볼드 | 291 | hh:mm · 프로그램 · 구분선 · hh:mm · 프로그램 · 구분선 |
| `sec/bold/list/15` | list-bold-15 | 나열-볼드 | 볼드 | 426 | hh:mm 프로그램 진행자 · hh:mm 프로그램 진행자 · hh:mm 프로그램 진행자 |
| `sec/bold/story/04` | story-bold-04 | 스토리-볼드 | 볼드 | 136 | “문장형 카피를 입력합니다.” — |
| `sec/bold/story/05` | story-bold-05 | 스토리-볼드 | 볼드 | 228 | “ · 문장형 카피를 입력합니다. · “ |
| `sec/editorial/hero/10` | hero-editorial-10 | 히어로-에디토리얼 | 에디토리얼 | 124 | 프로필 이미지 · 이름 한 줄 소개 |
| `sec/editorial/hero/11` | hero-editorial-11 | 히어로-에디토리얼 | 에디토리얼 | 124 | 프로필 이미지 · 이름 한 줄 소개 |
| `sec/editorial/hero/12` | hero-editorial-12 | 히어로-에디토리얼 | 에디토리얼 | 192 | 문장형 카피를 입력합니다 · —— |
| `sec/editorial/hero/13` | hero-editorial-13 | 히어로-에디토리얼 | 에디토리얼 | 363 | EYEBROW · 문장형 카피를 입력합니다 · LABEL 세부 정보 · LABEL 세부 정보 · LABEL  |
| `sec/editorial/intro/06` | intro-editorial-06 | 소개-에디토리얼 | 에디토리얼 | 68 | label · 소개 문구 |
| `sec/editorial/key_info/06` | key_info-editorial-06 | 핵심 정보-에디토리얼 | 에디토리얼 | 126 | label 세부 정보 · label 세부 정보 · label 세부 정보 |
| `sec/editorial/key_info/07` | key_info-editorial-07 | 핵심 정보-에디토리얼 | 에디토리얼 | 93 | label · 세부 정보 추가 정보 |
| `sec/editorial/key_info/08` | key_info-editorial-08 | 핵심 정보-에디토리얼 | 에디토리얼 | 205 | label · 세부 정보 추가 정보 · label · 세부 정보 추가 정보 · 구분선 · *부가 설명 텍스트 |
| `sec/editorial/purchase/04` | purchase-editorial-04 | 구매-에디토리얼 | 에디토리얼 | 202 | 00% OFF · 상품명 · (용량 / 원산지) · 정상가 00,000원 · → 00,000원 |
| `sec/editorial/purchase/05` | purchase-editorial-05 | 구매-에디토리얼 | 에디토리얼 | 226 | 00% OFF · 상품명 · (용량 / 원산지) · 정상가 00,000원 · → 00,000원 · (추가할인 |
| `sec/editorial/purchase/06` | purchase-editorial-06 | 구매-에디토리얼 | 에디토리얼 | 194 | 00% OFF · 상품명 · (용량 / 원산지) · 정상가 00,000원 → 00,000원 · (추가할인조건 |
| `sec/minimal/hero/06` | hero-minimal-06 | 히어로-미니멀 | 미니멀 | 277 | 프로필 이미지 · 이름 · 한 줄 설명 |
| `sec/minimal/hero/07` | hero-minimal-07 | 히어로-미니멀 | 미니멀 | 247 | 프로필 이미지 · 이름 · 한 줄 설명 |
| `sec/minimal/list/08` | list-minimal-08 | 나열-미니멀 | 미니멀 | 204 | YYYY.MM – YYYY.MM · 회사명 · 소속 · 역할 · YYYY.MM – YYYY.MM · 회사명  |
| `sec/minimal/list/09` | list-minimal-09 | 나열-미니멀 | 미니멀 | 162 | 00 label · 세부 정보 · 00 label · 세부 정보 · 00 label · 세부 정보 |
| `sec/minimal/materials/03` | materials-minimal-03 | 자료-미니멀 | 미니멀 | 164 | 이미지 · LABEL · 소개 문구 |
| `sec/minimal/materials/04` | materials-minimal-04 | 자료-미니멀 | 미니멀 | 164 | LABEL · 소개 문구 · 이미지 |
| `sec/minimal/materials/05` | materials-minimal-05 | 자료-미니멀 | 미니멀 | 347 | 이미지 · LABEL · 소개 문구 |
| `sec/minimal/story/03` | story-minimal-03 | 스토리-미니멀 | 미니멀 | 142 | 문장형 카피를 입력합니다 · —— |
| `sec/mixed/hero/01` | hero-mixed-01 | 히어로-미에 | 미니멀+에디토리얼 | 416 | EYEBROW · 페이지 제목 · 카피 혹은 소개 문구 · 이미지 |
| `sec/mixed/hero/02` | hero-mixed-02 | 히어로-미에 | 미니멀+에디토리얼 | 460 | 메인 비주얼 · EYEBROW 페이지 제목 카피 |
| `sec/mixed/hero/03` | hero-mixed-03 | 히어로-미에 | 미니멀+에디토리얼 | 256 | 메인 비주얼 · 페이지 제목 카피 혹은 설명 문구 |
| `sec/mixed/hero/04` | hero-mixed-04 | 히어로-에볼 | 에디토리얼+볼드 | 786 | 로고 · 카피 혹은 소개 문구 · 혜택 및 핵심 정보 · 문장형 카피를 입력합니다 · 카피 혹은 소개 문구  |
| `sec/mixed/hero/05` | hero-mixed-05 | 히어로-에볼 | 에디토리얼+볼드 | 940 | EYEBROW · 페이지 제목 · 한 줄 행사 설명 · 메인 이미지 · LABEL · 세부 정보 |
| `sec/mixed/intro/03` | intro-mixed-03 | 소개-미에볼 | 미니멀+에디토리얼+볼드 | 68 | 소개 문구 |
| `sec/mixed/intro/04` | intro-mixed-04 | 소개-미에볼 | 미니멀+에디토리얼+볼드 | 104 | 초대의 글 · ○○○ 드림 |
| `sec/mixed/intro/05` | intro-mixed-05 | 소개-미에볼 | 미니멀+에디토리얼+볼드 | 108 | 구분선 · 소개 문구 · 구분선 |
| `sec/mixed/key_info/03` | key_info-mixed-03 | 핵심 정보-미에 | 미니멀+에디토리얼 | 170 | label · 세부 정보 · label · 세부 정보 |
| `sec/mixed/key_info/04` | key_info-mixed-04 | 핵심 정보-미에 | 미니멀+에디토리얼 | 222 | label · 세부 정보 · 추가 정보 · label · 세부 정보 · 추가 정보 |
| `sec/mixed/key_info/08` | key_info-mixed-08 | 핵심 정보-미볼 | 미니멀+볼드 | 155 | label 세부 정보 추가 정보 |
| `sec/mixed/key_info/09` | key_info-mixed-09 | 핵심 정보-미볼 | 미니멀+볼드 | 155 | label 세부 정보 추가 정보 |
| `sec/mixed/key_info/10` | key_info-mixed-10 | 핵심 정보-미볼 | 미니멀+볼드 | 132 | label 세부 정보 · label 세부 정보 |
| `sec/mixed/key_info/11` | key_info-mixed-11 | 핵심 정보-미볼 | 미니멀+볼드 | 132 | label 세부 정보 · label 세부 정보 · label 세부 정보 |
| `sec/mixed/list/03` | list-mixed-03 | 나열-미에 | 미니멀+에디토리얼 | 219 | ● · YYYY 이력 내용 · ● · YYYY 이력 내용 · ● · YYYY 이력 내용 |
| `sec/mixed/list/04` | list-mixed-04 | 나열-미에 | 미니멀+에디토리얼 | 218 | YYYY.DD · 이력 내용 · 구분선 · 이력 내용 · YYYY.DD · 구분선 |
| `sec/mixed/list/16` | list-mixed-16 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | 156 | YYYY · 이력 내용 · YYYY · 이력 내용 · YYYY · 이력 내용 |
| `sec/mixed/list/17` | list-mixed-17 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | 205 | YYYY.DD · 이력 내용 · 구분선 · YYYY.DD · 이력 내용 · 구분선 |
| `sec/mixed/list/18` | list-mixed-18 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | 156 | hh:mm · 프로그램 · hh:mm · 프로그램 · hh:mm · 프로그램 |
| `sec/mixed/list/19` | list-mixed-19 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | 231 | hh:mm · 프로그램 진행자 · hh:mm · 프로그램 진행자 · hh:mm · 프로그램 진행자 |
| `sec/mixed/list/20` | list-mixed-20 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | 225 | hh:mm · 내용 · hh:mm · 내용 · hh:mm · 내용 |
| `sec/mixed/list/21` | list-mixed-21 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | 248 | label · 항목 · 세부 정보 · 항목 · 세부 정보 · label |
| `sec/mixed/list/22` | list-mixed-22 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | 310 | label · 항목 · 세부 정보 · 항목 · 세부 정보 · label |
| `sec/mixed/list/23` | list-mixed-23 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | 251 | label · 항목 · 세부 정보 · 항목 · 세부 정보 · 구분선 |
| `sec/mixed/list/24` | list-mixed-24 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | 150 | 아이콘 · label 세부 정보 · 아이콘 · label 세부 정보 |
| `sec/mixed/list/25` | list-mixed-25 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | 210 | label 세부 정보 · → · label 세부 정보 · → |
| `sec/mixed/list/26` | list-mixed-26 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | 116 | 메뉴1 · 메뉴2 · 메뉴3 · 메뉴4 · 메뉴5 · 메뉴6 |
| `sec/mixed/list/27` | list-mixed-27 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | 116 | 메뉴1 · 메뉴2 · 메뉴3 · 메뉴4 · 메뉴5 · 메뉴6 |
| `sec/mixed/materials/03` | materials-mixed-03 | 자료-미에 | 미니멀+에디토리얼 | 384 | 이미지 · LABEL 소개 문구 · LABEL 소개 문구 · 이미지 |
| `sec/mixed/notice/04` | notice-mixed-04 | 안내사항-에볼 | 에디토리얼+볼드 | 240 | 00 · 질문 · 답변 · 00 · 질문 · 답변 |
| `sec/mixed/notice/07` | notice-mixed-07 | 안내사항-미에볼 | 미니멀+에디토리얼+볼드 | 176 | Q · 질문 · A · 답변 · Q · 질문 |
| `sec/mixed/notice/08` | notice-mixed-08 | 안내사항-미에볼 | 미니멀+에디토리얼+볼드 | 193 | 질문 · 답변 · 구분선 · 질문 · 답변 |
| `sec/mixed/story/04` | story-mixed-04 | 스토리-미에 | 미니멀+에디토리얼 | 136 | “문장형 카피를 입력합니다.” — |

---

## B. 키(번호) 변경 37개

내용은 그대로고 **번호만** 바뀐다. 어드민 상세 패널의 「프리셋 키」를 고치고 **메타 저장**.

🔴 **충돌 주의** — 번호가 **커지는** 묶음은 **큰 번호부터**, **작아지는** 묶음은 **작은 번호부터** 실행해야 기존 키와 겹치지 않는다.

### sec/bold/key_info — 4건 (번호 감소 → **작은 번호부터**)

| 순서 | 현재 키 | 새 키 | 서랍 |
|---|---|---|---|
| 1 | `sec/bold/key_info/05` | `sec/bold/key_info/04` | 핵심 정보-볼드 |
| 2 | `sec/bold/key_info/06` | `sec/bold/key_info/05` | 핵심 정보-볼드 |
| 3 | `sec/bold/key_info/07` | `sec/bold/key_info/06` | 핵심 정보-볼드 |
| 4 | `sec/bold/key_info/08` | `sec/bold/key_info/07` | 핵심 정보-볼드 |

### sec/editorial/key_info — 5건 (번호 감소 → **작은 번호부터**)

| 순서 | 현재 키 | 새 키 | 서랍 |
|---|---|---|---|
| 1 | `sec/editorial/key_info/02` | `sec/editorial/key_info/01` | 핵심 정보-에디토리얼 |
| 2 | `sec/editorial/key_info/03` | `sec/editorial/key_info/02` | 핵심 정보-에디토리얼 |
| 3 | `sec/editorial/key_info/04` | `sec/editorial/key_info/03` | 핵심 정보-에디토리얼 |
| 4 | `sec/editorial/key_info/05` | `sec/editorial/key_info/04` | 핵심 정보-에디토리얼 |
| 5 | `sec/editorial/key_info/06` | `sec/editorial/key_info/05` | 핵심 정보-에디토리얼 |

### sec/mixed/hero — 1건 (번호 증가 → **큰 번호부터**)

| 순서 | 현재 키 | 새 키 | 서랍 |
|---|---|---|---|
| 1 | `sec/mixed/hero/03` | `sec/mixed/hero/06` | 히어로-미에볼 |

### sec/mixed/key_info — 5건 (번호 증가 → **큰 번호부터**)

| 순서 | 현재 키 | 새 키 | 서랍 |
|---|---|---|---|
| 1 | `sec/mixed/key_info/07` | `sec/mixed/key_info/13` | 핵심 정보-에볼 |
| 2 | `sec/mixed/key_info/06` | `sec/mixed/key_info/12` | 핵심 정보-에볼 |
| 3 | `sec/mixed/key_info/05` | `sec/mixed/key_info/07` | 핵심 정보-미볼 |
| 4 | `sec/mixed/key_info/04` | `sec/mixed/key_info/06` | 핵심 정보-미볼 |
| 5 | `sec/mixed/key_info/03` | `sec/mixed/key_info/05` | 핵심 정보-미볼 |

### sec/mixed/list — 11건 (번호 증가 → **큰 번호부터**)

| 순서 | 현재 키 | 새 키 | 서랍 |
|---|---|---|---|
| 1 | `sec/mixed/list/13` | `sec/mixed/list/15` | 나열-미에볼 |
| 2 | `sec/mixed/list/12` | `sec/mixed/list/14` | 나열-미에볼 |
| 3 | `sec/mixed/list/11` | `sec/mixed/list/13` | 나열-미에볼 |
| 4 | `sec/mixed/list/10` | `sec/mixed/list/12` | 나열-미에볼 |
| 5 | `sec/mixed/list/09` | `sec/mixed/list/11` | 나열-미에볼 |
| 6 | `sec/mixed/list/08` | `sec/mixed/list/10` | 나열-미에볼 |
| 7 | `sec/mixed/list/07` | `sec/mixed/list/09` | 나열-미에볼 |
| 8 | `sec/mixed/list/06` | `sec/mixed/list/08` | 나열-에볼 |
| 9 | `sec/mixed/list/05` | `sec/mixed/list/07` | 나열-에볼 |
| 10 | `sec/mixed/list/04` | `sec/mixed/list/06` | 나열-에볼 |
| 11 | `sec/mixed/list/03` | `sec/mixed/list/05` | 나열-미볼 |

### sec/mixed/materials — 8건 (번호 증가 → **큰 번호부터**)

| 순서 | 현재 키 | 새 키 | 서랍 |
|---|---|---|---|
| 1 | `sec/mixed/materials/10` | `sec/mixed/materials/11` | 자료-미에볼 |
| 2 | `sec/mixed/materials/09` | `sec/mixed/materials/10` | 자료-미에볼 |
| 3 | `sec/mixed/materials/08` | `sec/mixed/materials/09` | 자료-미에볼 |
| 4 | `sec/mixed/materials/07` | `sec/mixed/materials/08` | 자료-미에볼 |
| 5 | `sec/mixed/materials/06` | `sec/mixed/materials/07` | 자료-미에볼 |
| 6 | `sec/mixed/materials/05` | `sec/mixed/materials/06` | 자료-미에볼 |
| 7 | `sec/mixed/materials/04` | `sec/mixed/materials/05` | 자료-미에볼 |
| 8 | `sec/mixed/materials/03` | `sec/mixed/materials/04` | 자료-미에볼 |

### sec/mixed/notice — 2건 (번호 증가 → **큰 번호부터**)

| 순서 | 현재 키 | 새 키 | 서랍 |
|---|---|---|---|
| 1 | `sec/mixed/notice/05` | `sec/mixed/notice/06` | 안내사항-미에볼 |
| 2 | `sec/mixed/notice/04` | `sec/mixed/notice/05` | 안내사항-미에볼 |

### sec/mixed/story — 1건 (번호 증가 → **큰 번호부터**)

| 순서 | 현재 키 | 새 키 | 서랍 |
|---|---|---|---|
| 1 | `sec/mixed/story/04` | `sec/mixed/story/05` | 스토리-미에볼 |

---

## C. 어드민에서 제거 4개 — 피그마에 없음

피그마에서 삭제된 프리셋인데 어드민에는 게시된 채 남아 있다. **B의 번호 변경이 이 자리를 쓰므로 먼저 처리**해야 한다.

| 어드민 키 | 옛 피그마 노드 | 비고 |
|---|---|---|
| `sec/bold/key_info/04` | 5395:14347 | 이 자리를 지금의 `key_info-bold-04`가 차지한다 |
| `sec/editorial/key_info/01` | 5395:14210 | 이 자리를 지금의 `key_info-editorial-01`이 차지한다 |
| `sec/mixed/hero/01` | 5455:111 | 히어로 에볼 2개가 새 프리셋으로 교체됨 |
| `sec/mixed/hero/02` | 5455:128 | 히어로 에볼 2개가 새 프리셋으로 교체됨 |

> 「보관하기」로 내리는 것을 권장(삭제 이력 보존). 게시 상태로 두면 랜덤 선택에서 없는 프리셋이 뽑힌다.

---

## D. 내용이 달라진 듯 — 확인 필요 3개

키는 그대로지만 **피그마 쪽 카드 구성이 어드민 등록본과 다르다.** 피그마가 정본이면 **에디터에서 다시 저장(재등록)** 해야 한다.

| 키 | 피그마 이름 | 어드민 블록 | 피그마 카드 | 차이 |
|---|---|---|---|---|
| `sec/editorial/materials/02` | materials-editorial-02 | 3 (텍스트·이미지·갤러리) | 4 (텍스트·갤러리×3) | 이미지 → 갤러리로 바뀌고 1개 늘어남 |
| `sec/mixed/materials/06` | materials-mixed-06 | 9 | 10 | 구분선 배치가 다름 |
| `sec/mixed/materials/07` | materials-mixed-07 | 9 | 10 | 구분선 배치가 다름 |

> 참고: `sec/editorial/intro/01·02`, `sec/mixed/promo/04·11`도 숫자가 달라 보이지만 **피그마 쪽 묶음 프레임(2열 카드·래퍼) 때문**이라 실제로는 같다.

---

## 변경 없음

- **헤더 17 · 푸터 36 · 섹션 타이틀 12 = 65개 전부 그대로** (번호·개수·블록 수 일치).
- 섹션 프리셋 중 258개는 키 그대로.

## 참고

- 어드민 키 편집 위치: 프리셋 클릭 → 우측 패널 **「프리셋 키」** 입력 → **메타 저장**. 같은 패널에서 **레이아웃 태그**·**섹션 목적**·**보관하기**도 가능.
- 대조 근거 데이터: `preset-index/preset-index.json`(피그마 355) ↔ 어드민 `/api/ai/presets`(299).