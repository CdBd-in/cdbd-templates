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
  FP=$(printf '%s|%s' "$T" "$BT" | cksum | cut -d' ' -f1)
  [ "$FP" = "$PREV" ] && REP=$((REP+1)) || REP=0; PREV="$FP"
  [ "$REP" -ge 2 ] && { log "STUCK(지문 3회 동일) — 자동 우회 안 함 · 중단"; snap stuck; exit 2; }
  if [ "$(clickBtn '다음')" != "ok" ]; then
    [ "$(clickBtn '이건 없어요')" != "ok" ] && { log "STOP: 진행 버튼 없음"; snap nobtn; exit 4; }
  fi
  sleep 3
done
log "마지막 확인: $(body 500)"; snap final-check
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
