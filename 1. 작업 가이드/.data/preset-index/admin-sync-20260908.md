---
title: AI 프리셋 어드민 ↔ 피그마 대조 — 섹션 순서 할 일 (2026-09-08)
type: worklist
---

# AI 프리셋 어드민 업데이트 — 섹션 순서 할 일 (2026-09-08)

> 어드민 `/admin/ai/presets` **299개** ↔ 피그마 「섹션 프리셋」 34:23 **355개** 전수 대조.
> **어드민 키의 번호 = 피그마 캔버스 순서(그룹 위→아래, 카드 왼→오른쪽)** — 오늘 정리한 피그마 번호와 같은 규칙이다. 그래서 차이는 전부 **삽입·이동으로 인한 번호 밀림**뿐이다.

## 전체 요약

| 작업 | 건수 |
|---|---|
| 🔑 키(번호) 수정 | **41** (그중 4건은 서랍이 바뀐 것) |
| ➕ 신규 등록 | **56** |
| 🗑 삭제 | **0** — 없어진 줄 알았던 4개는 전부 살아있고 옮겨진 것 |
| 변경 없음 | 258 + 헤더17·푸터36·타이틀12 |

⚠️ **각 섹션 안에서는 아래 번호 순서대로** 키를 고쳐야 기존 키와 충돌하지 않는다. 키 수정을 다 끝낸 뒤 신규 등록.

### 살아있는 4개 (예전 「삭제 대상」 정정)

| 어드민 현재 키 | → 새 키 | 무슨 일이 있었나 |
|---|---|---|
| `sec/editorial/key_info/01` | `sec/mixed/key_info/03` | 에디토리얼 서랍 → **미에**(미니멀+에디토리얼)로 이동 |
| `sec/bold/key_info/04` | `sec/mixed/key_info/10` | 볼드 서랍 → **미볼**(미니멀+볼드)로 이동 |
| `sec/mixed/hero/01` | `sec/mixed/hero/04` | 서랍 그대로(에볼), 앞에 미에 3개가 생겨 밀림 |
| `sec/mixed/hero/02` | `sec/mixed/hero/05` | 서랍 그대로(에볼), 앞에 미에 3개가 생겨 밀림 |

> 피그마에서 노드 번호(id)가 새로 생겨 「없어진 것」으로 보였지만, 높이·구성 슬롯이 완전히 같아 동일 섹션으로 확인.

---

## 히어로 — 키 수정 3 · 신규 11

### ① 키 수정 (이 순서대로)

| # | 현재 키 | → 새 키 | 비고 |
|---|---|---|---|
| 1 | `sec/mixed/hero/03` | `sec/mixed/hero/06` | 번호 밀림 (히어로-미에볼) |
| 2 | `sec/mixed/hero/01` | `sec/mixed/hero/04` | 서랍 그대로(에볼) · 앞에 미에 3개가 생겨 번호만 밀림 |
| 3 | `sec/mixed/hero/02` | `sec/mixed/hero/05` | 서랍 그대로(에볼) · 앞에 미에 3개가 생겨 번호만 밀림 |

### ② 신규 등록

| 새 키 | 피그마 이름 | 서랍 | 레이아웃 태그 | 담는 칸 |
|---|---|---|---|---|
| `sec/bold/hero/09` | hero-bold-09 | 히어로-볼드 | 볼드 | 프로필 이미지 · 이름 · 한 줄 설명 |
| `sec/bold/hero/10` | hero-bold-10 | 히어로-볼드 | 볼드 | 메인 비주얼 · 페이지 제목 카피 혹은 설명 문구 · 버튼 텍스트 |
| `sec/editorial/hero/10` | hero-editorial-10 | 히어로-에디토리얼 | 에디토리얼 | 프로필 이미지 · 이름 한 줄 소개 |
| `sec/editorial/hero/11` | hero-editorial-11 | 히어로-에디토리얼 | 에디토리얼 | 프로필 이미지 · 이름 한 줄 소개 |
| `sec/editorial/hero/12` | hero-editorial-12 | 히어로-에디토리얼 | 에디토리얼 | 문장형 카피를 입력합니다 · —— |
| `sec/editorial/hero/13` | hero-editorial-13 | 히어로-에디토리얼 | 에디토리얼 | EYEBROW · 문장형 카피를 입력합니다 · LABEL 세부 정보 · LABEL 세부 정보 · LABEL  |
| `sec/minimal/hero/06` | hero-minimal-06 | 히어로-미니멀 | 미니멀 | 프로필 이미지 · 이름 · 한 줄 설명 |
| `sec/minimal/hero/07` | hero-minimal-07 | 히어로-미니멀 | 미니멀 | 프로필 이미지 · 이름 · 한 줄 설명 |
| `sec/mixed/hero/01` | hero-mixed-01 | 히어로-미에 | 미니멀+에디토리얼 | EYEBROW · 페이지 제목 · 카피 혹은 소개 문구 · 이미지 |
| `sec/mixed/hero/02` | hero-mixed-02 | 히어로-미에 | 미니멀+에디토리얼 | 메인 비주얼 · EYEBROW 페이지 제목 카피 |
| `sec/mixed/hero/03` | hero-mixed-03 | 히어로-미에 | 미니멀+에디토리얼 | 메인 비주얼 · 페이지 제목 카피 혹은 설명 문구 |

## 소개 — 키 수정 0 · 신규 5

### ① 신규 등록

| 새 키 | 피그마 이름 | 서랍 | 레이아웃 태그 | 담는 칸 |
|---|---|---|---|---|
| `sec/bold/intro/04` | intro-bold-04 | 소개-볼드 | 볼드 | 소개 문구 |
| `sec/editorial/intro/06` | intro-editorial-06 | 소개-에디토리얼 | 에디토리얼 | label · 소개 문구 |
| `sec/mixed/intro/03` | intro-mixed-03 | 소개-미에볼 | 미니멀+에디토리얼+볼드 | 소개 문구 |
| `sec/mixed/intro/04` | intro-mixed-04 | 소개-미에볼 | 미니멀+에디토리얼+볼드 | 초대의 글 · ○○○ 드림 |
| `sec/mixed/intro/05` | intro-mixed-05 | 소개-미에볼 | 미니멀+에디토리얼+볼드 | 구분선 · 소개 문구 · 구분선 |

## 핵심 정보 — 키 수정 16 · 신규 7

### ① 키 수정 (이 순서대로)

| # | 현재 키 | → 새 키 | 비고 |
|---|---|---|---|
| 1 | `sec/mixed/key_info/06` | `sec/mixed/key_info/12` | 번호 밀림 (핵심 정보-에볼) |
| 2 | `sec/mixed/key_info/07` | `sec/mixed/key_info/13` | 번호 밀림 (핵심 정보-에볼) |
| 3 | `sec/bold/key_info/04` | `sec/mixed/key_info/10` | **서랍 이동** 볼드 → 미볼 · 레이아웃 태그에 **미니멀 추가** |
| 4 | `sec/bold/key_info/05` | `sec/bold/key_info/04` | 번호 밀림 (핵심 정보-볼드) |
| 5 | `sec/bold/key_info/06` | `sec/bold/key_info/05` | 번호 밀림 (핵심 정보-볼드) |
| 6 | `sec/bold/key_info/07` | `sec/bold/key_info/06` | 번호 밀림 (핵심 정보-볼드) |
| 7 | `sec/bold/key_info/08` | `sec/bold/key_info/07` | 번호 밀림 (핵심 정보-볼드) |
| 8 | `sec/mixed/key_info/04` | `sec/mixed/key_info/06` | 번호 밀림 (핵심 정보-미볼) |
| 9 | `sec/mixed/key_info/05` | `sec/mixed/key_info/07` | 번호 밀림 (핵심 정보-미볼) |
| 10 | `sec/mixed/key_info/03` | `sec/mixed/key_info/05` | 번호 밀림 (핵심 정보-미볼) |
| 11 | `sec/editorial/key_info/01` | `sec/mixed/key_info/03` | **서랍 이동** 에디토리얼 → 미에 · 레이아웃 태그에 **미니멀 추가** |
| 12 | `sec/editorial/key_info/02` | `sec/editorial/key_info/01` | 번호 밀림 (핵심 정보-에디토리얼) |
| 13 | `sec/editorial/key_info/03` | `sec/editorial/key_info/02` | 번호 밀림 (핵심 정보-에디토리얼) |
| 14 | `sec/editorial/key_info/04` | `sec/editorial/key_info/03` | 번호 밀림 (핵심 정보-에디토리얼) |
| 15 | `sec/editorial/key_info/05` | `sec/editorial/key_info/04` | 번호 밀림 (핵심 정보-에디토리얼) |
| 16 | `sec/editorial/key_info/06` | `sec/editorial/key_info/05` | 번호 밀림 (핵심 정보-에디토리얼) |

### ② 신규 등록

| 새 키 | 피그마 이름 | 서랍 | 레이아웃 태그 | 담는 칸 |
|---|---|---|---|---|
| `sec/editorial/key_info/06` | key_info-editorial-06 | 핵심 정보-에디토리얼 | 에디토리얼 | label 세부 정보 · label 세부 정보 · label 세부 정보 |
| `sec/editorial/key_info/07` | key_info-editorial-07 | 핵심 정보-에디토리얼 | 에디토리얼 | label · 세부 정보 추가 정보 |
| `sec/editorial/key_info/08` | key_info-editorial-08 | 핵심 정보-에디토리얼 | 에디토리얼 | label · 세부 정보 추가 정보 · label · 세부 정보 추가 정보 · 구분선 · *부가 설명 텍스트 |
| `sec/mixed/key_info/04` | key_info-mixed-04 | 핵심 정보-미에 | 미니멀+에디토리얼 | label · 세부 정보 · 추가 정보 · label · 세부 정보 · 추가 정보 |
| `sec/mixed/key_info/08` | key_info-mixed-08 | 핵심 정보-미볼 | 미니멀+볼드 | label 세부 정보 추가 정보 |
| `sec/mixed/key_info/09` | key_info-mixed-09 | 핵심 정보-미볼 | 미니멀+볼드 | label 세부 정보 추가 정보 |
| `sec/mixed/key_info/11` | key_info-mixed-11 | 핵심 정보-미볼 | 미니멀+볼드 | label 세부 정보 · label 세부 정보 · label 세부 정보 |

## 스토리 — 키 수정 1 · 신규 4

### ① 키 수정 (이 순서대로)

| # | 현재 키 | → 새 키 | 비고 |
|---|---|---|---|
| 1 | `sec/mixed/story/04` | `sec/mixed/story/05` | 번호 밀림 (스토리-미에볼) |

### ② 신규 등록

| 새 키 | 피그마 이름 | 서랍 | 레이아웃 태그 | 담는 칸 |
|---|---|---|---|---|
| `sec/bold/story/04` | story-bold-04 | 스토리-볼드 | 볼드 | “문장형 카피를 입력합니다.” — |
| `sec/bold/story/05` | story-bold-05 | 스토리-볼드 | 볼드 | “ · 문장형 카피를 입력합니다. · “ |
| `sec/minimal/story/03` | story-minimal-03 | 스토리-미니멀 | 미니멀 | 문장형 카피를 입력합니다 · —— |
| `sec/mixed/story/04` | story-mixed-04 | 스토리-미에 | 미니멀+에디토리얼 | “문장형 카피를 입력합니다.” — |

## 안내사항 — 키 수정 2 · 신규 3

### ① 키 수정 (이 순서대로)

| # | 현재 키 | → 새 키 | 비고 |
|---|---|---|---|
| 1 | `sec/mixed/notice/05` | `sec/mixed/notice/06` | 번호 밀림 (안내사항-미에볼) |
| 2 | `sec/mixed/notice/04` | `sec/mixed/notice/05` | 번호 밀림 (안내사항-미에볼) |

### ② 신규 등록

| 새 키 | 피그마 이름 | 서랍 | 레이아웃 태그 | 담는 칸 |
|---|---|---|---|---|
| `sec/mixed/notice/04` | notice-mixed-04 | 안내사항-에볼 | 에디토리얼+볼드 | 00 · 질문 · 답변 · 00 · 질문 · 답변 |
| `sec/mixed/notice/07` | notice-mixed-07 | 안내사항-미에볼 | 미니멀+에디토리얼+볼드 | Q · 질문 · A · 답변 · Q · 질문 |
| `sec/mixed/notice/08` | notice-mixed-08 | 안내사항-미에볼 | 미니멀+에디토리얼+볼드 | 질문 · 답변 · 구분선 · 질문 · 답변 |

## 나열 — 키 수정 11 · 신규 19

### ① 키 수정 (이 순서대로)

| # | 현재 키 | → 새 키 | 비고 |
|---|---|---|---|
| 1 | `sec/mixed/list/12` | `sec/mixed/list/14` | 번호 밀림 (나열-미에볼) |
| 2 | `sec/mixed/list/13` | `sec/mixed/list/15` | 번호 밀림 (나열-미에볼) |
| 3 | `sec/mixed/list/10` | `sec/mixed/list/12` | 번호 밀림 (나열-미에볼) |
| 4 | `sec/mixed/list/11` | `sec/mixed/list/13` | 번호 밀림 (나열-미에볼) |
| 5 | `sec/mixed/list/08` | `sec/mixed/list/10` | 번호 밀림 (나열-미에볼) |
| 6 | `sec/mixed/list/09` | `sec/mixed/list/11` | 번호 밀림 (나열-미에볼) |
| 7 | `sec/mixed/list/06` | `sec/mixed/list/08` | 번호 밀림 (나열-에볼) |
| 8 | `sec/mixed/list/07` | `sec/mixed/list/09` | 번호 밀림 (나열-미에볼) |
| 9 | `sec/mixed/list/04` | `sec/mixed/list/06` | 번호 밀림 (나열-에볼) |
| 10 | `sec/mixed/list/05` | `sec/mixed/list/07` | 번호 밀림 (나열-에볼) |
| 11 | `sec/mixed/list/03` | `sec/mixed/list/05` | 번호 밀림 (나열-미볼) |

### ② 신규 등록

| 새 키 | 피그마 이름 | 서랍 | 레이아웃 태그 | 담는 칸 |
|---|---|---|---|---|
| `sec/bold/list/13` | list-bold-13 | 나열-볼드 | 볼드 | YYYY · 이력 내용 · 구분선 · YYYY · 이력 내용 · 구분선 |
| `sec/bold/list/14` | list-bold-14 | 나열-볼드 | 볼드 | hh:mm · 프로그램 · 구분선 · hh:mm · 프로그램 · 구분선 |
| `sec/bold/list/15` | list-bold-15 | 나열-볼드 | 볼드 | hh:mm 프로그램 진행자 · hh:mm 프로그램 진행자 · hh:mm 프로그램 진행자 |
| `sec/minimal/list/08` | list-minimal-08 | 나열-미니멀 | 미니멀 | YYYY.MM – YYYY.MM · 회사명 · 소속 · 역할 · YYYY.MM – YYYY.MM · 회사명  |
| `sec/minimal/list/09` | list-minimal-09 | 나열-미니멀 | 미니멀 | 00 label · 세부 정보 · 00 label · 세부 정보 · 00 label · 세부 정보 |
| `sec/mixed/list/03` | list-mixed-03 | 나열-미에 | 미니멀+에디토리얼 | ● · YYYY 이력 내용 · ● · YYYY 이력 내용 · ● · YYYY 이력 내용 |
| `sec/mixed/list/04` | list-mixed-04 | 나열-미에 | 미니멀+에디토리얼 | YYYY.DD · 이력 내용 · 구분선 · 이력 내용 · YYYY.DD · 구분선 |
| `sec/mixed/list/16` | list-mixed-16 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | YYYY · 이력 내용 · YYYY · 이력 내용 · YYYY · 이력 내용 |
| `sec/mixed/list/17` | list-mixed-17 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | YYYY.DD · 이력 내용 · 구분선 · YYYY.DD · 이력 내용 · 구분선 |
| `sec/mixed/list/18` | list-mixed-18 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | hh:mm · 프로그램 · hh:mm · 프로그램 · hh:mm · 프로그램 |
| `sec/mixed/list/19` | list-mixed-19 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | hh:mm · 프로그램 진행자 · hh:mm · 프로그램 진행자 · hh:mm · 프로그램 진행자 |
| `sec/mixed/list/20` | list-mixed-20 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | hh:mm · 내용 · hh:mm · 내용 · hh:mm · 내용 |
| `sec/mixed/list/21` | list-mixed-21 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | label · 항목 · 세부 정보 · 항목 · 세부 정보 · label |
| `sec/mixed/list/22` | list-mixed-22 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | label · 항목 · 세부 정보 · 항목 · 세부 정보 · label |
| `sec/mixed/list/23` | list-mixed-23 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | label · 항목 · 세부 정보 · 항목 · 세부 정보 · 구분선 |
| `sec/mixed/list/24` | list-mixed-24 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | 아이콘 · label 세부 정보 · 아이콘 · label 세부 정보 |
| `sec/mixed/list/25` | list-mixed-25 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | label 세부 정보 · → · label 세부 정보 · → |
| `sec/mixed/list/26` | list-mixed-26 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | 메뉴1 · 메뉴2 · 메뉴3 · 메뉴4 · 메뉴5 · 메뉴6 |
| `sec/mixed/list/27` | list-mixed-27 | 나열-미에볼 | 미니멀+에디토리얼+볼드 | 메뉴1 · 메뉴2 · 메뉴3 · 메뉴4 · 메뉴5 · 메뉴6 |

## 자료 — 키 수정 8 · 신규 4

### ① 키 수정 (이 순서대로)

| # | 현재 키 | → 새 키 | 비고 |
|---|---|---|---|
| 1 | `sec/mixed/materials/10` | `sec/mixed/materials/11` | 번호 밀림 (자료-미에볼) |
| 2 | `sec/mixed/materials/09` | `sec/mixed/materials/10` | 번호 밀림 (자료-미에볼) |
| 3 | `sec/mixed/materials/08` | `sec/mixed/materials/09` | 번호 밀림 (자료-미에볼) |
| 4 | `sec/mixed/materials/07` | `sec/mixed/materials/08` | 번호 밀림 (자료-미에볼) |
| 5 | `sec/mixed/materials/06` | `sec/mixed/materials/07` | 번호 밀림 (자료-미에볼) |
| 6 | `sec/mixed/materials/05` | `sec/mixed/materials/06` | 번호 밀림 (자료-미에볼) |
| 7 | `sec/mixed/materials/04` | `sec/mixed/materials/05` | 번호 밀림 (자료-미에볼) |
| 8 | `sec/mixed/materials/03` | `sec/mixed/materials/04` | 번호 밀림 (자료-미에볼) |

### ② 신규 등록

| 새 키 | 피그마 이름 | 서랍 | 레이아웃 태그 | 담는 칸 |
|---|---|---|---|---|
| `sec/minimal/materials/03` | materials-minimal-03 | 자료-미니멀 | 미니멀 | 이미지 · LABEL · 소개 문구 |
| `sec/minimal/materials/04` | materials-minimal-04 | 자료-미니멀 | 미니멀 | LABEL · 소개 문구 · 이미지 |
| `sec/minimal/materials/05` | materials-minimal-05 | 자료-미니멀 | 미니멀 | 이미지 · LABEL · 소개 문구 |
| `sec/mixed/materials/03` | materials-mixed-03 | 자료-미에 | 미니멀+에디토리얼 | 이미지 · LABEL 소개 문구 · LABEL 소개 문구 · 이미지 |

## 예약

할 일 없음.

## 폼

할 일 없음.

## 구매 — 키 수정 0 · 신규 3

### ① 신규 등록

| 새 키 | 피그마 이름 | 서랍 | 레이아웃 태그 | 담는 칸 |
|---|---|---|---|---|
| `sec/editorial/purchase/04` | purchase-editorial-04 | 구매-에디토리얼 | 에디토리얼 | 00% OFF · 상품명 · (용량 / 원산지) · 정상가 00,000원 · → 00,000원 |
| `sec/editorial/purchase/05` | purchase-editorial-05 | 구매-에디토리얼 | 에디토리얼 | 00% OFF · 상품명 · (용량 / 원산지) · 정상가 00,000원 · → 00,000원 · (추가할인 |
| `sec/editorial/purchase/06` | purchase-editorial-06 | 구매-에디토리얼 | 에디토리얼 | 00% OFF · 상품명 · (용량 / 원산지) · 정상가 00,000원 → 00,000원 · (추가할인조건 |

## 프로모션

할 일 없음.

## 위치 안내

할 일 없음.

## 문의

할 일 없음.

---

## 변경 없음

- 헤더 17 · 푸터 36 · 섹션 타이틀 12 = **65개 전부 그대로**(번호·블록 수 일치).
- 예약 · 폼 · 프로모션 · 위치 안내 · 문의 = **할 일 없음**.

## 작업 방법

어드민에서 섹션 클릭 → 우측 패널 **「프리셋 키」** 수정 → **메타 저장**. 같은 패널에서 **레이아웃 태그**도 수정.
신규 등록은 에디터(프리뷰 도메인)에서 **프리셋 설정 → 프리셋 저장**.

대조 근거: `preset-index/preset-index.json`(피그마 355) ↔ 어드민 `/api/ai/presets`(299) · 살아있는 295개 중 288개는 블록 수까지 일치.