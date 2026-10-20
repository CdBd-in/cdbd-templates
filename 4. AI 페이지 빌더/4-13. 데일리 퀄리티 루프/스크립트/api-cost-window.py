#!/usr/bin/env python3
# AI 빌더 「한 사이클」 API 원가 측정 — 시간 구간의 토큰 사용량을 Anthropic 사용량 API로 읽어 원가 계산
#
# 사용법:
#   ANTHROPIC_ADMIN_KEY=sk-ant-admin-... python3 api-cost-window.py "2026-10-21T02:00:00+09:00" "2026-10-21T02:10:00+09:00"
#
# 준비물: Anthropic Console(cdbdin@gmail.com) → Settings → Organization → Admin keys 에서 발급한 Admin 키.
#   (일반 API 키로는 조직 사용량 조회가 안 됨 — 읽기 전용이라 과금·생성에는 쓰이지 않는다)
#
# 실험 절차 (조용한 시간대 권장 — 다른 트래픽이 섞이면 과대 측정):
#   1) 시작 시각 기록 → s2run.sh <ID> "<설명>" 1회 실행 → 종료 시각 기록
#   2) 이 스크립트에 [시작-1분, 종료+1분] 구간을 넣어 실행
#   3) 3회 반복해 중앙값 채택
import json, os, sys, urllib.request, urllib.parse

KEY = os.environ.get("ANTHROPIC_ADMIN_KEY")
if not KEY or len(sys.argv) < 3:
    print(__doc__ or "usage"); print("필요: ANTHROPIC_ADMIN_KEY 환경변수 + 시작/종료 시각 (RFC3339)"); sys.exit(1)
START, END = sys.argv[1], sys.argv[2]

# USD/1M tokens: (input, output). 캐시 쓰기 = input×1.25(5분)/×2(1시간), 캐시 읽기 = input×0.1
PRICES = {
    "fable-5":    (10.0, 50.0),
    "opus":       (5.0, 25.0),    # opus-5 / 4.8 / 4.7 / 4.6 동일
    "sonnet-5":   (2.0, 10.0),
    "sonnet-4-6": (3.0, 15.0),
    "sonnet":     (3.0, 15.0),    # 기타 sonnet 폴백
    "haiku":      (1.0, 5.0),
}
def price_for(model):
    for k, v in PRICES.items():
        if k in (model or ""): return v
    return (5.0, 25.0)  # 모름 → opus 단가로 보수적 추정

def fetch(page=None):
    q = {"starting_at": START, "ending_at": END, "bucket_width": "1m", "limit": 1440}
    url = "https://api.anthropic.com/v1/organizations/usage_report/messages?" + urllib.parse.urlencode(q)
    url += "&group_by[]=model"
    if page: url += "&page=" + urllib.parse.quote(page)
    req = urllib.request.Request(url, headers={"x-api-key": KEY, "anthropic-version": "2023-06-01"})
    return json.load(urllib.request.urlopen(req))

totals = {}  # model -> dict
page = None
while True:
    resp = fetch(page)
    for bucket in resp.get("data", []):
        for r in bucket.get("results", []):
            m = r.get("model") or "unknown"
            t = totals.setdefault(m, {"in": 0, "cw": 0, "cr": 0, "out": 0})
            t["in"] += r.get("uncached_input_tokens", 0) or 0
            cc = r.get("cache_creation")
            if isinstance(cc, dict):
                t["cw"] += (cc.get("ephemeral_5m_input_tokens", 0) or 0) + (cc.get("ephemeral_1h_input_tokens", 0) or 0)
            else:
                t["cw"] += r.get("cache_creation_input_tokens", 0) or 0
            t["cr"] += r.get("cache_read_input_tokens", 0) or 0
            t["out"] += r.get("output_tokens", 0) or 0
    if resp.get("has_more") and resp.get("next_page"):
        page = resp["next_page"]
    else:
        break

if not totals:
    print(f"구간 {START} ~ {END} 에 사용량 없음 (키가 다른 조직이거나, 사이클이 이 구간 밖에서 돌았거나)"); sys.exit(0)

KRW = 1450  # 환율 — 필요 시 수정
grand = 0.0
print(f"구간: {START} ~ {END}\n")
for m, t in totals.items():
    pin, pout = price_for(m)
    usd = (t["in"] * pin + t["cw"] * pin * 1.25 + t["cr"] * pin * 0.1 + t["out"] * pout) / 1_000_000
    grand += usd
    print(f"[{m}] 입력 {t['in']:,} · 캐시쓰기 {t['cw']:,} · 캐시읽기 {t['cr']:,} · 출력 {t['out']:,} → ${usd:.4f}")
print(f"\n합계: ${grand:.4f} ≈ ₩{grand*KRW:,.0f}")
