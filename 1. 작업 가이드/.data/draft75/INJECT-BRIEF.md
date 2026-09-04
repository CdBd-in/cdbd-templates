# 이미지 Figma 주입 가이드 (2026-09-04)

fileKey `24O01lprp5i2ufl7CbZXXx` · 대상 페이지 `5843:37`
이미지 = `images/<코드>/*.png` + `images/<코드>/manifest.json`

## 🔑 절대 원칙
**같은 주제의 3안(미니멀·에디토리얼·볼드)은 「완전히 같은 이미지」를 쓴다** (이선호 지시).
→ 반드시 **같은 `imageHash`** 를 3안에 적용할 것. 같은 파일을 3번 업로드하면 해시가 달라질 수 있으니 **1회 업로드 → 해시 회수 → 3안에 복사**.

## 절차
### 1단계 — 업로드 (안1에 직접 꽂기)
`upload_assets` 를 `count`와 `nodeIds`로 호출하면 **업로드 이미지를 그 노드의 fill로 바로 설정**해 준다.
```
upload_assets(fileKey, count:N, nodeIds:[안1의 슬롯 노드 ID ...], scaleMode:"FILL")
→ 반환된 각 uploadUrl 에 curl 로 PNG 바이트 POST
   curl -X POST --data-binary @파일.png -H "Content-Type: image/png" "<uploadUrl>"
```
- 한 번에 **최대 60개**. 다음 호출 전에 반환된 URL에 **전부 POST**할 것.

### 2단계 — 해시 회수 후 안2·안3에 복사
```js
// 안1 슬롯에서 해시 읽기
const h = node1.fills.find(f=>f.type==="IMAGE").imageHash;
// 안2·안3의 대응 슬롯에 같은 해시 적용
node2.fills=[{type:"IMAGE", imageHash:h, scaleMode:"FILL"}];
for(const c of (node2.children||[])) c.visible=false;   // "이미지" 라벨 텍스트 숨김
```
⚠️ **로고는 `scaleMode:"FIT"`** (잘리면 안 됨). 사진·화보는 `"FILL"`.

## 슬롯 매핑 규칙
| manifest 키 | 어디에 |
|---|---|
| `hero` | 히어로 섹션의 **가장 큰 이미지** placeholder (`메인 이미지`·`메인 비주얼`·`이미지`) |
| `logo` | **헤더·푸터의 로고** 슬롯 (`로고`) · `scaleMode:"FIT"` |
| `logo_light` | **다크 배경 안**(배경 명도 낮음)의 로고에만. 밝은 안은 `logo` |
| `profile`·`profile1~N` | `프로필 이미지` 슬롯 (인물형·연사) |
| `sq1~N` / `p1_1~` / `L1_1~` / `prod`·`proc`·`desc` | 갤러리·자료·상품 컷 — **문서 순서대로** 차례로 |
| `story` | 스토리·소개 섹션의 이미지 |

- **manifest에 없는 슬롯은 placeholder 그대로 둔다**(억지로 채우지 말 것 — 페르소나가 자료가 없는 것이 설정).
- 이미지가 슬롯보다 적으면 **남는 슬롯은 그대로**. 많으면 **앞에서부터** 쓰고 남는 건 버림.
- 🚫 **지도(`지도 임베드`)는 건드리지 말 것** — 이미 전용 해시가 들어가 있거나 별도 처리 대상.

## ⚠️ 슬롯 찾을 때 주의
- `characters` 주입 때문에 **TEXT 노드 이름이 내용으로 바뀐 것들이 섞여 있다.** 반드시 **`n.type!=="TEXT"` 이고 `fills`에 SOLID가 있고 IMAGE가 없는 노드**만 후보로.
- 이름 후보: `이미지`·`메인 이미지`·`메인 비주얼`·`프로필 이미지`·`로고`·`키비주얼`
- **바깥 프레임 + 안쪽 RECT 쌍**으로 된 경우가 많다 → **실제 보이는 쪽(안쪽 RECT)에 fill을 넣어야** 화면에 나온다. 프레임에만 넣으면 자식 RECT가 덮어 안 보인다.
- 적용 후 **반드시 스크린샷으로 실제 보이는지 확인**할 것.

## 🚨 병렬 작업 중
- 🚫 `figma.setCurrentPageAsync()` 금지 · `page.children` 전체 순회 수정 금지 — **자기 담당 주제 프레임만**
- read-only 오류 시 30초 간격 3회만 재시도 후 보고·종료
