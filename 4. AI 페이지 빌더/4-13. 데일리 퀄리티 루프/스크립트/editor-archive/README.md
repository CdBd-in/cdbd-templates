# 에디터 산출물 아카이브 캡처 (2026-10-22)

S2로 만든 CdBd 에디터 페이지를 **2장**으로 캡처한다.
① `{id}-preview.png` — 미리보기를 끝까지 스크롤해 이어붙인 **전체 페이지**(폭 364)
② `{id}-editor.png` — **카드 목록이 전부 보이는** 에디터 화면(폭 1680 · 카드 수에 맞춰 뷰포트 높이 자동 확장)

## 쓰는 법
```bash
export BROWSE_STATE_FILE=/tmp/browse-arch-state.json   # 다른 browse 작업과 격리
# 1) 프리뷰 도메인 로그인 (.env의 CDBD_EMAIL/PASSWORD · 비밀번호 칸에서 Enter)
# 2) 캡처
./capture.sh 6990          # → /tmp/arch/out/6990-{preview,editor}.png
```
결과·로그 = `/tmp/arch/out` · `/tmp/arch/status.txt`(OK / FAIL_OPEN / FAIL_STITCH)

## 알아 둘 것
- 미리보기 스크롤 컨테이너 = `div.absolute.inset-0.overflow-y-scroll` (페이지 전체에서 유일한 스크롤 영역)
- 카드 보드는 `height: calc(100vh-212px)`라 **뷰포트를 키우면 카드가 더 보인다** → 스크립트가 `scrollHeight-clientHeight`만큼 뷰포트를 늘린 뒤 찍는다
- 스티치는 **세그먼트마다 실제 `scrollTop`을 기록**해 겹치는 만큼 잘라 붙인다(마지막 칸 중복 방지)
- 🚫 이미지 git 커밋 금지 — 보관은 피그마(🗄 레퍼런스 아카이브 › 🧪 S2 빌더 산출물)
- ⚠️ 에디터는 사라진다. 리포트를 쓸 때 **그 호에서 바로** 캡처할 것
