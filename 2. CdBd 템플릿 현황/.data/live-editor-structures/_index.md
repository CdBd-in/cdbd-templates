# 라이브 18개 에디터 구조 → 피그마 빌드 (2026-07-03)

> https://www.cdbd.in/templates 각 템플릿 "템플릿 사용하기" → 에디터 → 구조 추출 → 피그마 빌드.
> 피그마: CdBd 템플릿 등록 파일 페이지 "기존 18개 · 에디터 구조" (node-id 900-23).

## 최종 빌드 아키텍처 (사용자 피드백 반영 확정)
1. **프레임 width = 380** (카드 = FILL 폭).
2. **페이지·카드 전부 오토레이아웃** (page = 세로 auto-layout, 각 카드 = auto-layout 프레임). 배경 있는 인셋 섹션은 외부여백 wrapper + 내부 fill 프레임 2-depth.
3. **하나의 텍스트 카드 = 하나의 텍스트 박스**. 카드 내 여러 스타일 행을 병합해 range로 폰트·크기·색을 다르게 주고, **행 line-height = 다음 행과의 y차이**로 원본 세로 간격 재현.
4. **페이지 배경색** 실제 테마값 적용 (예: seminar #fafafa, popup #a23721, recruit #16161a). 다크 페이지는 카드 투명, 라이트 페이지는 흰 글씨 카드에 다크 fill.
5. **폰트: 요소별 computed font-family를 Figma 폰트로 매핑** (Pretendard 일괄 금지). 매핑: Pretendard / Bebas Neue / ChosunilboNM / Cafe24 ClassicType OTF / Playfair Display / KoPub Batang(=GounBatang 대체) / KoPubWorldDotum_Pro / Anton / Montserrat / Noto Serif KR(serif fallback).
6. 이미지·갤러리·프로필·지도 = 회색 `[타입]` 플레이스홀더 (C-이미지). Q&A = 폼(체크박스·입력창·제출 pill) absolute-in-frame. 버튼/예약/CTA = pill.

## 재사용 파이프라인
- 추출: `extract_abs.js` (카드 rect + computed style + font-family) → `abs2_*.json`
- 변환: `transform3.py` (raw → 타입별 모델 `nb_*.json`)
- 빌드: 범용 오토레이아웃 빌더 (`builder.js` 참조) + 모델 embed → use_figma

## 초대·예약 (7)
| # | slug | 에디터 | 카드 | 폰트 | 피그마 |
|---|---|---|---|---|---|
| 1 | invitation/seminar | 5018 | 25 | Pretendard | ✅ 934:23 (x0) |
| 2 | invitation/reservation | 5019 | 27 | Bebas+Chosun+Pretendard | ✅ 940:23 (x460) |
| 3 | invitation/rsvp | 5020 | 50 | Cafe24Classic+Pretendard | ✅ 941:23 (x920) |
| 4 | invitation/personalized | 5022 | 40 | Playfair+GounBatang(→KoPubBatang)+Pretendard | ✅ 938:23 (x1380) |
| 5 | invitation/popup-reservation | 5023 | 17 | Anton+Pretendard | ✅ 942:23 (x1840) |
| 6 | invitation/recruit-rsvp | 5024 | 16 | Montserrat+Pretendard | ✅ 943:23 (x2300) |
| 7 | invitation/(수강신청·반별예약) | - | - | - | 대기 |

⚠️ 에디터 인스턴스 5018~5024 = 분석용 신규 생성분 → 정리 대상 (CLAUDE.md TODO).
