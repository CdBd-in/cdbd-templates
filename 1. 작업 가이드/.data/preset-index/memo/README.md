# 프리셋 메모 도구 (2026-10-23)

어드민 프리셋 「메모」를 **[[4-13. 데일리 퀄리티 루프]] §4 고정 포맷**으로 만들고 넣는 도구. 2026-10-23 전 섹션(364) 기록에 썼다.

| 파일 | 하는 일 |
|---|---|
| `common.py` | 어드민 카드에서 글자 뽑기(`block_texts`) · 키 ↔ 피그마 이름 변환 |
| `align.py` | 어드민 키 ↔ 피그마 섹션 짝 맞추기 — **이름이 아니라 내용(카드 구성 + 글자)으로**, 그룹 안 순서를 지키며 정렬 |
| `tagger.py` · `tagger2.py` | 내용 태그(`content`) · 무게(`weight`) · 항목 수(`items`) · 쓰는 조건 판정 (`tagger2.analyze`가 최종판) |
| `figsig.txt` | 피그마 섹션 프레임의 카드 구성 기호(2026-10-23 스냅숏 · 섹션을 고치면 다시 뽑는다) |
| `bulk2.js` | 어드민 화면에서 메모 일괄 저장 — `window.__MEMO = {키: 메모}`(필요하면 `window.__only=[키…]`) 넣고 `browse eval` |

**어드민 저장 API** — `PATCH /api/ai/presets/{키}` · 본문 `{"notes", "layout_styles"}` + **`title_variant`는 문자열일 때만**(null을 보내면 400 「title_variant must be a string」) · 로그인한 프리뷰 도메인 화면 안에서 `fetch`. 저장해도 게시 상태는 그대로.

**순서** — ① `editor-audit/dump.sh --presets <폴더>`로 어드민 목록 받기(`PRESETS_JSON`) ② 새 섹션이면 피그마 구성 기호를 `figsig.txt`에 추가 ③ `align.build()` → `tagger2.analyze()` → 서랍별로 사람이 훑어 고치기 ④ `bulk2.js`로 저장 → 다시 받아 대조 ⑤ 피그마 원본에 같은 내용 「프리셋 메모」 주석(분류 id `8263:0`) ⑥ 색인 `preset-index.json`의 `key`·`content`·`weight`·`items_range`·`use_when` 갱신.
