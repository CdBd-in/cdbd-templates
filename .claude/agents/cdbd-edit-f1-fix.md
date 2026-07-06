---
name: cdbd-edit-f1-fix
description: CdBd 파이프라인 F1 — diff 배열을 받아 CdBd 에디터에서 실제 수정·영속화. block 참조를 직접 변경하고 reorder-commit으로 autosave. 정렬버튼·패널 트리거는 커밋 안 됨(검증됨).
---

먼저 `.claude/cdbd-edit-shared.md`를 읽는다.

## 입력
`editorId` · diff 배열(각 `cardId`·`field`·`expected`·`howToFix`). 여러 카드 diff를 한 번에 받을 수 있음.

## 🔑 영속화 원리 (editor 5025 검증 2026-07-06)
CdBd 수정은 **block 객체를 참조로 직접 변경 → reorder-commit**으로 저장한다.
- ❌ **안 되는 것**: 정렬버튼/패널 컨트롤을 `.click()`(synthetic)이나 `$B click`(real)해도 **커밋 안 됨** — 리로드하면 원복. (그 핸들러는 다른 블록 참조를 씀.)
- ✅ **되는 것**: `reorderCard`의 `onDragEnd`가 `n({...l, blocks})`로 **실제 blocks 배열(내가 바꾼 참조 포함)을 재직렬화·autosave**. 그래서 참조를 mutate한 뒤 reorder를 한 번 태우면 모든 변경이 영속된다.

## 절차
1. 드라이버 설치 확인(`window.__cdbd`). **카드 선택 불필요**(참조 변경 방식).
2. **참조 변경 (배치 — 커밋 전 모두 적용):** diff마다
   - `var blk = window.__cdbd.blockById('<cardId>')`.
   - **텍스트 디자인**(fontSize/color/lineHeight/textAlign/fontFamily/bold): `blk.style`의 키를 `expected`로, **그리고 `blk.content`(Lexical JSON 문자열)를 `JSON.parse` → 모든 `text` 노드 inline `style`(및 paragraph `textStyle`)의 해당 속성을 expected로, bold는 `format` 비트 → `JSON.stringify`로 `blk.content` 재대입**. (렌더는 content 기준 → content 갱신 필수.)
   - **비텍스트**(이미지/구분선/갤러리/프로필 등): `blk.style`·`blk.divider`·`blk.gallery`·`blk.innerStyle`·`blk.profile` 등 해당 키 직접 변경.
   - 여러 diff·여러 카드를 **모두 참조 변경**해 둔다(한 번의 커밋으로 일괄 저장 가능 — 카드별 선택 반복 불필요).
3. **커밋(영속화) = reorder 라운드트립** (bash sleep 필수, 동기 2회 ❌):
   ```bash
   $B js "var o=window.__cdbd.cardOrder(); window.__cdbd.reorderCard(0, 1)"; sleep 1.3
   $B js "window.__cdbd.reorderCard(1, 0)"; sleep 1.3   # 순서 원복 + 두 번째 커밋
   ```
   (0/1이 고정 핀 카드면 다른 인접 비핀 쌍을 고른다.)
4. **검증**: `window.__cdbd.dumpState()` 재덤프 → 해당 diff 해소 확인. 확실히 하려면 리로드(`goto editor/{id}; sleep 6; eval driver`) 후 재확인 → autosave 영속 확인. 미해소는 재시도(≤2).

## 출력
`{applied:[{cardId,field}...], remaining:[{cardId,field}...]}` + 실행 위치 `https://www.cdbd.in/editor/{editorId}`.

## 설계 함의 (스펙 반영됨)
참조 변경 + 단일 reorder-commit이라 **카드별 선택이 불필요** → "수정=카드별"의 선택-최소화 근거는 약해지고, 실제로는 **모든 diff를 배치 mutate 후 1회 커밋**이 가장 효율적. (이미지 업로드 등 패널 필요한 수정만 예외.)
