# 75안 이미지 생성 브리프 (2026-09-04 이선호 지시)

## 원칙
1. 🔑 **주제 1개 = 이미지 1세트.** 그 주제의 **3안(미니멀·에디토리얼·볼드)이 전부 같은 이미지**를 쓴다.
   → 안마다 다른 이미지 ❌. 이미지는 **주제 단위 자산**이다.
2. 콘텐츠 JSON(`<코드>.json`)의 `persona.who` + `sections` 를 읽고 **그 페르소나의 실제 사업·상황에 맞는** 이미지를 만든다.
   (예 `1-③` = 청주 반찬가게 개업 → 반찬 진열대·간판 사진이지 스톡 느낌의 추상 이미지 ❌)
3. **한국 배경·한국인**이 기본. 인물은 `Realistic Korean facial features` + `candid documentary` + `soft natural light` 를 프롬프트에 반드시 넣는다 (안 넣으면 동남아·일본인이 생성됨).
4. 실재 브랜드 로고·상표·유명인 얼굴 ❌. 간판 글자는 페르소나의 지어낸 상호로.

## 생성 도구
OpenAI `gpt-image-1` · 키 = `~/.config/cdbd/credentials.json` 의 `openai_api_key`
```bash
KEY=$(python3 -c "import json;print(json.load(open('$HOME/.config/cdbd/credentials.json'))['openai_api_key'])")
curl -s https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"gpt-image-1","prompt":"...","size":"1024x1024","n":1}' \
  | python3 -c "import sys,json,base64;d=json.load(sys.stdin);open('out.png','wb').write(base64.b64decode(d['data'][0]['b64_json']))"
```
- 가로형은 `"size":"1536x1024"` · 세로형은 `"1024x1536"` · 정사각은 `"1024x1024"`
- 실패하면 3회까지 재시도, 계속 실패하면 그 슬롯은 건너뛰고 manifest에 기록

## 슬롯 종류 (필요한 것만 만든다 — 콘텐츠에 없으면 만들지 말 것)
| 키 | 용도 | 비율 | 개수 |
|---|---|---|---|
| `hero` | 히어로 메인 비주얼 | 3:2 가로 | 1 |
| `sq1`~`sqN` | 갤러리·자료·상품 컷 | 1:1 | 콘텐츠의 실제 항목 수만큼 (최대 6) |
| `profile` | 인물 사진 (P6 인물형·연사·대표) | 1:1 | 필요한 만큼 (최대 4) |
| `logo` | 워드마크 로고 | 4:1 가로 | 1 (로고가 있는 페르소나만) |

🚫 **지도는 만들지 말 것** — 기존 고정 이미지를 쓴다.
🚫 로고가 없는 페르소나(`4-⑤`·`6-①`·`2-①`·`2-④` 등)는 `logo` 생성 ❌.

## 로고 만들 때
- **투명 배경 워드마크**(상호 글자만). 심볼은 단순 도형 1개까지.
- 프롬프트에 `flat vector wordmark logo, transparent background, single solid color, no gradient, no 3D, centered`
- 생성 후 **알파 바운딩 박스로 크롭**(투명 여백 제거) — PIL `alpha.getbbox()`

## 산출물
`1. 작업 가이드/.data/draft75/images/<코드>/` 에 PNG를 저장하고,
`images/<코드>/manifest.json` 에 아래 형식으로 기록:
```json
{"code":"1-①",
 "images":[
   {"key":"hero","file":"hero.png","w":1536,"h":1024,"prompt":"...","용도":"히어로 메인 비주얼"},
   {"key":"sq1","file":"sq1.png","w":1024,"h":1024,"prompt":"...","용도":"행사장 전경"}
 ]}
```
파일명은 코드에 원문자를 쓰지 말고 폴더는 `1-1`·`4-6` 형식으로.
