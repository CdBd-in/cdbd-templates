#!/bin/bash
# S2 JS 드라이버 — snapshot 접근성 트리가 빈 값을 반환하는 빌드 대응 (2026-10-22)
# 사용: s2js.sh <사례ID> "<설명>"
B="$HOME/.claude/skills/gstack/browse/dist/browse"
export BROWSE_STATE_FILE="${BROWSE_STATE_FILE:-/tmp/browse-s2-state.json}"
ID="$1"; DESC="$2"
AR="${S2_AR:?S2_AR 필요}"; FR="$AR/$ID-frames"; mkdir -p "$AR" "$FR"
LOG="$AR/$ID-log.txt"; : > "$LOG"; T0=$(date +%s)
log(){ echo "[$(( $(date +%s)-T0 ))s] $*" | tee -a "$LOG"; }
j(){ $B js "$1" 2>/dev/null | tail -1; }
guard(){ case "$($B url 2>/dev/null)" in *ai-makevu-s-team.vercel.app*) return 0;;
  *) log "ABORT(세션 이탈): $($B url)"; exit 3;; esac; }
btns(){ j "JSON.stringify([...document.querySelectorAll('button')].map(e=>e.innerText.replace(/\s+/g,' ').trim()||e.getAttribute('aria-label')||''))"; }
# 글자 버튼 + 아이콘 버튼(aria-label) 모두 매칭 — 「보내기」·「자료 첨부」는 아이콘뿐이라 innerText 가 빈 값
clickBtn(){ j "(()=>{const n='$1';const b=[...document.querySelectorAll('button')].find(e=>!e.disabled&&(e.innerText.replace(/\s+/g,' ').trim()===n||e.getAttribute('aria-label')===n));if(!b)return 'no';b.click();return 'ok';})()"; }
body(){ j "document.body.innerText.replace(/\s+/g,' ').slice(0,${1:-160})"; }
snap(){ $B screenshot "$FR/$(date +%s)-$1.png" --viewport >/dev/null 2>&1; }

# ── 「전부 채우기」 모드 (2026-10-26 신설) ─────────────────────────────────
# S2_ANSWERS=<TSV 파일> 이 있으면 텍스트 칸을 우리 답변으로 채우고,
# S2_IMAGES=<폴더> 가 있으면 이미지 칸에 업로드한다. 둘 다 없으면 기존처럼 건너뛴다.
#
# 답변 TSV 형식: 한 줄 = `패턴<TAB>값`
#   · 패턴 = grep -E 정규식. 매칭 대상 = "화면 첫 90자(헤딩)|칸 라벨" (예: "구독 안내.*\|제목")
#   · 값 = 칸에 타이핑할 글. 줄바꿈은 \n 으로.
#   · 윗줄부터 먼저 매칭되고, 쓴 줄은 소진된다(같은 라벨 여러 번 → 줄을 여러 개).
#   · 매칭 없는 칸 = AI가 미리 채운 값 그대로 둔다(기존 동작).
# 이미지 폴더: 파일명(숫자·구분자 뗀 줄기)이 화면 글에 들어가면 그 파일 우선,
#   아니면 이름순으로 아직 안 쓴 파일. 다 쓰면 「이건 없어요」.
FILLWORK=""
if [ -n "${S2_ANSWERS:-}" ] && [ -f "$S2_ANSWERS" ]; then
  FILLWORK="/tmp/s2answers-work-$ID.tsv"; cp "$S2_ANSWERS" "$FILLWORK"
  log "채우기 모드: 답변 $(grep -c . "$FILLWORK")줄${S2_IMAGES:+ · 이미지 $(ls "${S2_IMAGES}" 2>/dev/null | wc -l | tr -d ' ')장}"
fi
IMGUSED="/tmp/s2imgused-$ID.txt"; : > "$IMGUSED"

# 현재 화면의 활성 칸: "text<TAB>라벨" / "image" / "none"
# 라벨 = label>span → aria-label → 조상 3단 안의 짧은(≤20자) span 순서로 추출
fieldinfo(){ j "(()=>{const t=[...document.querySelectorAll('textarea,input:not([type=file])')].find(e=>e.offsetParent&&!e.readOnly);if(t){let lb=t.closest('label')?.querySelector('span')?.innerText.trim()||t.getAttribute('aria-label')||'';if(!lb){let p=t;for(let k=0;k<3&&p;k++){p=p.parentElement;const s=p?.querySelector('span');const tx=(s?.innerText||'').trim();if(tx&&tx.length<=20){lb=tx;break;}}}return 'text\t'+lb;}const drop=/이 곳을 클릭하거나/.test(document.body.innerText)&&!!document.querySelector('input[type=file]');return drop?'image':'none';})()"; }

# 🔑 매칭 2단 (2026-10-26 라이브 검증에서 교정) — 화면 머리글엔 그룹의 「모든 칸 이름」이
#    같이 나와서(상품명·가격·설명 문구…) 머리글로 매칭하면 엉뚱한 칸에 들어간다(실측: 가격→설명 문구).
#    ① 1패스 = 패턴을 「칸 라벨」에만 매칭 (기본 — 패턴은 라벨 이름으로 쓸 것)
#    ② 2패스 = 패턴에 \| 가 있거나(문맥 한정형: 「구독 안내.*\|제목」) 라벨이 빈 칸만 「머리글|라벨」로 매칭
fill_text(){ # $1=라벨
  [ -z "$FILLWORK" ] && return 1
  local lb="$1" key n pat val pass
  key="$(body 90)|$lb"
  for pass in 1 2; do
    n=0
    while IFS=$'\t' read -r pat val; do
      n=$((n+1)); [ -z "$pat" ] || [ -z "$val" ] && continue
      if [ "$pass" = 1 ]; then
        [ -n "$lb" ] || continue
        printf '%s' "$lb" | grep -qE "$pat" || continue
      else
        case "$pat" in *'\|'*) :;; *) [ -z "$lb" ] || continue;; esac
        printf '%s' "$key" | grep -qE "$pat" || continue
      fi
      local v; v=$(printf '%b' "$val")
      $B fill 'textarea' "$v" >/dev/null 2>&1 || $B fill 'input:not([type=file])' "$v" >/dev/null 2>&1
      sed -i '' "${n}d" "$FILLWORK"   # 쓴 줄 소진
      log "  ↳ 채움[${lb:-무라벨}]: $(printf '%s' "$v" | head -1 | cut -c1-40)"
      return 0
    done < "$FILLWORK"
  done
  return 1
}

fill_image(){ # 인자 없음 · 화면 글(헤딩) 키워드 → 파일명 우선, 아니면 이름순 미사용분
  [ -n "${S2_IMAGES:-}" ] && [ -d "$S2_IMAGES" ] || return 1
  local H f="" x bn stem
  H=$(body 90)
  for x in "$S2_IMAGES"/*; do
    [ -f "$x" ] || continue; bn=$(basename "$x")
    grep -qxF "$bn" "$IMGUSED" && continue
    stem=$(printf '%s' "$bn" | sed 's/\.[^.]*$//; s/^[0-9 _-]*//')
    [ -n "$stem" ] && case "$H" in *"$stem"*) f="$bn"; break;; esac
  done
  if [ -z "$f" ]; then
    for x in "$S2_IMAGES"/*; do
      [ -f "$x" ] || continue; bn=$(basename "$x")
      grep -qxF "$bn" "$IMGUSED" || { f="$bn"; break; }
    done
  fi
  [ -z "$f" ] && return 1
  $B upload 'input[type=file]' "$S2_IMAGES/$f" >/dev/null 2>&1 || return 1
  echo "$f" >> "$IMGUSED"; log "  ↳ 이미지 업로드: $f"
  return 0
}
# ────────────────────────────────────────────────────────────────────────

$B goto "https://cdbd-client-git-ai-makevu-s-team.vercel.app/ai/create" >/dev/null 2>&1; sleep 6
guard
$B fill 'textarea' "$DESC" >/dev/null 2>&1
[ -n "$($B js "document.querySelector('textarea')?.value" 2>/dev/null | tail -1)" ] || { log "FAIL: 설명 입력 실패"; exit 1; }
sleep 1; SENT=$(clickBtn "보내기"); log "보내기 클릭=$SENT"
[ "$SENT" = "ok" ] || { log "FAIL: 보내기 버튼 없음 — 버튼목록=$(btns)"; exit 1; }
for w in $(seq 1 12); do sleep 3; case "$(body 80)" in *"이런 페이지 같은데"*|*"맞나요"*) break;; esac; done
log "설명 확인: $(body 160)"

# 확인 화면들
for i in $(seq 1 10); do
  guard; H=$(body 120); log "확인$i: $H"
  case "$H" in *"시안 제작 중"*|*"구성하고"*|*"채우고 있"*) break;; esac
  # 🔁 「다음」이 잠깐 사라지는 재렌더 구간이 있다 — 바로 포기하지 말고 재시도 (2026-10-22)
  CK=$(clickBtn '다음')
  if [ "$CK" != "ok" ]; then
    for rt in 1 2 3 4; do
      sleep 4; guard
      case "$(body 120)" in *"구성하고"*|*"채우고 있"*|*"제작 중"*) CK=gen; break;; esac
      CK=$(clickBtn '다음'); [ "$CK" = "ok" ] && break
    done
  fi
  [ "$CK" = "ok" ] || { log "다음 없음(재시도 4회) → 생성 단계로 간주 · 버튼=$(btns)"; break; }
  sleep 5
done

# 첫 시안 폴링
OK=0; for i in $(seq 1 30); do guard
  case "$(btns)" in *'"시작하기"'*) OK=1; break;; esac; sleep 10; done
[ "$OK" = 0 ] && { log "FAIL: 「시작하기」 미등장"; exit 5; }
log "첫 시안 완료"; snap draft1; clickBtn "시작하기" >/dev/null; sleep 4

# 내용 채우기
PREV=""; REP=0
for i in $(seq 1 30); do
  guard; BT=$(btns)
  case "$BT" in *'"확인했어요"'*) break;; esac
  T=$(body 110); log "Q$i: $T"
  # S12 채점 입력 — 「입력 칸 ↔ 그 시점 미리보기」를 넘어가기 전에 떠 둔다 (읽기 전용)
  $B js "$(cat "$(dirname "$0")/fill-audit/snap.js")" 2>/dev/null | tail -1 >> "$AR/$ID-fill.jsonl"
  FP=$(printf '%s|%s' "$T" "$BT" | cksum | cut -d' ' -f1)
  [ "$FP" = "$PREV" ] && REP=$((REP+1)) || REP=0; PREV="$FP"
  [ "$REP" -ge 2 ] && { log "STUCK(지문 3회 동일) — 자동 우회 안 함 · 중단"; snap stuck; exit 2; }
  # 「전부 채우기」 — 답변·이미지가 준비돼 있으면 넘어가기 전에 채운다 (없으면 기존 건너뛰기)
  if [ -n "$FILLWORK" ] || [ -n "${S2_IMAGES:-}" ]; then
    FI=$(fieldinfo)
    case "$FI" in
      text*)  fill_text "${FI#text	}" && sleep 1.5;;
      image)  fill_image && sleep 2.5;;   # 업로드되면 「이건 없어요」가 「다음」으로 바뀐다
    esac
  fi
  if [ "$(clickBtn '다음')" != "ok" ]; then
    [ "$(clickBtn '이건 없어요')" != "ok" ] && { log "STOP: 진행 버튼 없음"; snap nobtn; exit 4; }
  fi
  sleep 3
done
log "마지막 확인: $(body 500)"; snap final-check
# S12 채점 — 내용 채우기 단계들의 입력↔미리보기 대조 (4-9-5 S12 · 결과는 리포트 결함 목록으로)
if [ -s "$AR/$ID-fill.jsonl" ]; then
  python3 "$(dirname "$0")/fill-audit/audit_fill.py" "$AR/$ID-fill.jsonl" 2>&1 | tee -a "$LOG" > "$AR/$ID-fill-audit.md"
  log "S12 채점: $(head -1 "$AR/$ID-fill-audit.md")"
fi
clickBtn "확인했어요" >/dev/null

# 3안 폴링 — 🎬 과정형 결함 대비 프레임 연속 캡처 (§0-8)
log "3안 생성 — 프레임 녹화 시작"
DONE=0
for i in $(seq 1 30); do
  guard; snap "3an-$(printf %02d $i)"
  ST=$(j "JSON.stringify([...document.querySelectorAll('*')].filter(e=>!e.children.length&&/제작 중|완료/.test(e.innerText)).map(e=>e.innerText.trim()).slice(0,6))")
  ER=$(j "(document.body.innerText.match(/문제가 생겼어요[^\n]*/)||[''])[0]")
  log "3안$i: $ST ${ER:+⚠️$ER}"
  case "$(btns)" in *'"3안 재생성"'*) DONE=1; break;; esac
  sleep 8
done
[ "$DONE" = 0 ] && { log "🔴 3안 미완료 — 진행 버튼 없음(막힘). 버튼=$(btns)"; snap 3an-blocked; exit 6; }
log "3안 완료"; snap 3drafts
clickBtn "시안 A" >/dev/null; sleep 2; clickBtn "다음" >/dev/null; sleep 5
log "무드: $(body 100)"; clickBtn "다음" >/dev/null
for i in $(seq 1 15); do sleep 10; case "$($B url)" in *editor*) break;; esac; done
log "에디터: $($B url)"

# 🔎 에디터 데이터 자동 검사 (4-9-5 S11 · editor-audit/) — 화면 채점이 놓치는 빈 줄·견본 값·여백 겹침을 데이터로 잡는다
#    실패해도 런 결과는 그대로(미측정으로 기록)
EID=$($B url 2>/dev/null | sed -n 's#.*/editor/\([0-9][0-9]*\).*#\1#p')
if [ -n "$EID" ]; then
  log "에디터 자동 검사: $EID"
  "$(dirname "$0")/editor-audit/run.sh" "$AR" "$EID" 2>&1 | tee -a "$LOG" || log "⚠️ 에디터 자동 검사 실패 — 미측정"
else
  log "⚠️ 에디터 ID 없음 — 자동 검사 미측정"
fi
exit 0
