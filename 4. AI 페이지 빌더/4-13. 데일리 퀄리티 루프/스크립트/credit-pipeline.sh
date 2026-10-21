#!/bin/bash
# 23:00 자동 측정 파이프라인 — 사례 2개(L4 채용공고 PDF 첨부+채우기 / L1b 요가 재실행) · 단계마다 콘솔 잔액 읽기 · 보고서 md 작성
S="$(cd "$(dirname "$0")" && pwd)"; AR="$S/../아카이브/$(date +%Y-%m-%d)/credit"; mkdir -p "$AR"
START="${START:-2300}"
until [ "$(date +%H%M)" -ge "$START" ]; do sleep 30; done
T0=$(date -u +%Y-%m-%dT%H:%M:00Z); echo "$T0" > "$AR/T0-night.txt"
rd(){ "$S/usage-read.sh" "$1" "$T0" | tee -a "$AR/night-reads.txt"; }
rd n00-baseline
# 사례 A — Lv4: 채용 공고 PDF 첨부 + 전부 채움
export ATTACH="$AR/wanted-383387.pdf" FILL=1
STAGE=1 "$S/credit-run.sh" L4 "개발자 채용 공고 페이지 제작. 공고 내용은 원티드에 올린 것 그대로. 공고 PDF 첨부." ; rd n01-L4-draft1
STAGE=2 "$S/credit-run.sh" L4 ; rd n02-L4-3drafts
STAGE=3 "$S/credit-run.sh" L4 ; rd n03-L4-editor
# 사례 B — Lv1 재실행: 요가(오늘과 동일 · 미입력)
unset ATTACH; export FILL=0
STAGE=1 "$S/credit-run.sh" L1b "요가 원데이 클래스 모집 페이지. 성수동 요가 스튜디오에서 매주 토요일 오전 10시 초보자 대상 90분 수업. 참가비 3만원, 매트 제공. 인스타그램 DM이나 전화로 예약." ; rd n04-L1b-draft1
STAGE=2 "$S/credit-run.sh" L1b ; rd n05-L1b-3drafts
STAGE=3 "$S/credit-run.sh" L1b ; rd n06-L1b-editor
sleep 240; rd n07-final
python3 - "$AR" <<'PY'
import json,glob,os,re,sys
ar=sys.argv[1]; rows=[]
for f in sorted(glob.glob(f"{ar}/credits-n*.json")):
    tag=os.path.basename(f)[8:-5]; rows.append((tag,json.load(open(f))['amount']/100))
out=["# 밤 11시 자동 측정 — 2사례 (콘솔 잔액 기준)","","| 지점 | 잔액 | 차감 |","|---|---|---|"]
for i,(t,a) in enumerate(rows):
    d=f"${rows[i-1][1]-a:.2f}" if i else "—"; out.append(f"| {t} | ${a:.2f} | {d} |")
if rows: out.append(f"\n**합계** ${rows[0][1]-rows[-1][1]:.2f}")
for c in ["L4","L1b"]:
    lg=f"{ar}/{c}-log.txt"
    if os.path.exists(lg):
        L=open(lg).read().splitlines(); out.append(f"\n## {c} 로그 요약"); out+=["- "+l for l in L if re.search(r"STAGE|완료|도착|첨부|STOP|FAIL|STUCK",l)]
open(f"{ar}/night-report.md","w").write("\n".join(out)); print("\n".join(out))
PY
