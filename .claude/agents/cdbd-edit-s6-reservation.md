---
name: cdbd-edit-s6-reservation
description: CdBd 파이프라인 S6 — 예약 정보. 예약 카드에 날짜·시간·정원·방문체크(필수)를 설정·저장. 크레딧 소모 스코프 — 부족 시 부분완료 리포트를 반환하고 파이프라인은 중단하지 않음. 직렬(브라우저 구동).
---

먼저 `.claude/cdbd-edit-shared.md`를 읽는다. 자동화는 skill `cdbd-card-automation` 사용.

## 담당
- 예약 카드의 **날짜·시간·정원·방문체크 종료** 설정·저장.
- 예약카드는 **예약 완료 1건당 1크레딧** 종량제. QR 방문체크는 별도 옵션(개발 중). SKU("풀패키지") 어휘 ❌ → "예약카드 QR 방문체크 옵션".

## 🔑 자동화 (skill 레시피)
- 예약 카드 추가는 **확인 다이얼로그 1단계 더**(S2와 동일; 이미 추가됐으면 생략).
- 예약 정보 모달: 날짜(MUI X DatePicker — `button[aria-label="Next month"]`/`"Previous month"` 직접), 시간, 정원, **방문체크 종료 필수**.
- 확정은 snapshot ref 실제 클릭(크레딧 확인 다이얼로그). skill `cdbd-card-automation#예약-정보`.

## 크레딧 부족 처리 (필수)
크레딧 없으면 **`{status:'partial', reason:'credit'}` 반환하고 파이프라인 중단 ❌** — 나머지 스코프는 계속 진행되게 한다.

## 자기검증
모달 닫힘 = 저장, 우측 패널 예약정보 표시. 크레딧 0이면 부분완료 명시.

## 출력
`{status:'ok'|'partial', reservations:[...], reason?}` + 실행 위치 `https://www.cdbd.in/editor/{editorId}`.
