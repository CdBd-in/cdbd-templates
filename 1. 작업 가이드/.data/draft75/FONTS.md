# Figma 로드 가능 폰트 — 75안 제작 실측 (2026-09-04)

⚠️ **CdBd 44종에 있어도 Figma에서 로드 안 되면 시안 제작 불가.** 아래 목록 안에서만 고를 것.

## ✅ 사용 가능 (한글)
| 폰트 | 사용 가능 웨이트 | 비고 |
|---|---|---|
| **Pretendard** | Thin~Black (9) | 🥇 안전 기본 · 본문 1순위 |
| **Noto Sans KR** | Thin~Black (7) | 본고딕 · 제목 가능 |
| **Noto Serif KR** | ExtraLight~Black (7) | 본명조 |
| **Gowun Batang** | Regular, **Bold** | 고운바탕 |
| **Gowun Dodum** | Regular만 | ⚠️ 명조 취급 — Gmarket·다른 명조와 조합 ❌ |
| **S-Core Dream** | **4 Regular · 7 ExtraBold만** | 🔴 6 Bold·3 Light 로드 불가 |
| **Gmarket Sans TTF** | **Bold · Light만** | 🔴 Regular/Medium 없음 → Bold나 Light로 매핑 |
| **NanumMyeongjo** | Regular, Bold, ExtraBold | |
| **NanumGothic** | Regular, Bold, ExtraBold | |
| **ChosunilboNM** | Regular만 | 조선일보명조 |
| **KoPub Batang** | Light, Regular, Bold | |
| **KoPubWorldDotum** | Medium, Bold | ⚠️ 본문 전용, 제목 ❌ |
| **Sunflower** | Light, Medium, Bold | |
| Song Myung / Do Hyeon / Jua / Black Han Sans / Stylish / Hahmlet | Regular(Hahmlet 9종) | 디스플레이 |

## 🚫 사용 금지
- **IBM Plex Sans KR** — Figma엔 있으나 **CdBd 44종에 없음** (4단계 재현 불가)
- 과잉 컨셉 10종 — Cafe24 Moyamoya · Bagel Fat One · Gaegu · Poor Story · East Sea Dokdo · Dokdo · Cute Font · Gugi · Dongle · Hi Melody · Gasoek One · Moirai One · Kirang Haerang · Yeon Sung · Nanum Brush Script · Nanum Pen · Grandiflora One · Single Day · Diphylleia

## ✅ 라틴 (전부 로드 가능)
Playfair Display · Cormorant · Libre Baskerville · EB Garamond · Lora · Marcellus ·
Inter · Montserrat · Poppins · DM Sans · Work Sans · Manrope · Outfit · Archivo ·
Space Grotesk · Syne · Josefin Sans · Bebas Neue · Oswald · Zeyada

## 웨이트 매핑 규칙 (프리셋 원본 웨이트 → 무드 폰트)
원본이 Bold/SemiBold → 그 패밀리의 가장 굵은 것 · 원본이 Regular/Medium → Regular 계열.
가용 웨이트가 2개뿐인 폰트(Gmarket·S-Core)는 **Bold↔Light / 7↔4** 두 단계로만.
