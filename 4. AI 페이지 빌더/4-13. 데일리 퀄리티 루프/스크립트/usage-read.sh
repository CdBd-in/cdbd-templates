#!/bin/bash
# 사용: usage-read.sh <tag> [window_start_utc ISO]   — Anthropic 콘솔(2번 탭, 로그인 상태) 1분 단위·모델별 사용량 + 크레딧 잔액
B="$HOME/.claude/skills/gstack/browse/dist/browse"
AR="/Users/leesunho/Documents/GitHub/design/cdbd-templates/4. AI 페이지 빌더/4-13. 데일리 퀄리티 루프/아카이브/$(date +%Y-%m-%d)/credit"; mkdir -p "$AR"
TAG="$1"; ST="${2:-$(date -u -v-30M +%Y-%m-%dT%H:%M:00Z)}"; EN=$(date -u -v+15M +%Y-%m-%dT%H:%M:00Z)
ORG=c4bcf9fd-1d18-4b71-8b5a-bf98a556e54f
H="{'accept':'application/json','anthropic-beta':'analytics-usage-cost-2026-08-24','anthropic-dangerous-direct-browser-access':'true','anthropic-version':'2023-06-01','x-organization-uuid':'$ORG'}"
$B tab ${CONSOLE_TAB:-2} >/dev/null 2>&1
$B js "fetch('/v1/organizations/analytics/usage?beta=true&starting_at=$ST&ending_at=$EN&time_bucket_width=1m&group_by[]=model&group_by[]=api_key_id&limit=5000',{headers:$H}).then(r=>r.text())" 2>/dev/null > "$AR/usage-$TAG.json"
$B js "fetch('/api/organizations/$ORG/prepaid/credits').then(r=>r.text())" 2>/dev/null > "$AR/credits-$TAG.json"
python3 - "$AR/usage-$TAG.json" "$AR/credits-$TAG.json" "$TAG" <<'PY'
import sys,json
u=json.load(open(sys.argv[1])); c=json.load(open(sys.argv[2])); tag=sys.argv[3]
print(f"[{tag}] 콘솔 크레딧 잔액 ${c['amount']/100:.2f} · data_refreshed_at={u.get('data_refreshed_at')}")
tot={}
for b in u['data']:
    g=b['group']; us=b['usage']; k=(g.get('model_display_name') or g.get('model'), g.get('api_key_name') or g.get('api_key_id'))
    t=tot.setdefault(k,{'req':0,'in':0,'c5m':0,'c1h':0,'cr':0,'out':0})
    t['req']+=us['requests']; t['in']+=us['uncached_input_tokens']; t['c5m']+=us['cache_creation']['ephemeral_5m_input_tokens']; t['c1h']+=us['cache_creation']['ephemeral_1h_input_tokens']; t['cr']+=us['cache_read_input_tokens']; t['out']+=us['output_tokens']
    print(f"  {b['starting_at'][11:16]}Z {k[0]} req={us['requests']} in={us['uncached_input_tokens']} cache_w={us['cache_creation']['ephemeral_5m_input_tokens']+us['cache_creation']['ephemeral_1h_input_tokens']} cache_r={us['cache_read_input_tokens']} out={us['output_tokens']}")
if not tot: print("  (창 안 사용량 0)")
for k,t in tot.items(): print(f"  합계 {k[0]} / key={k[1]}: req={t['req']} in={t['in']} cache_w5m={t['c5m']} cache_w1h={t['c1h']} cache_r={t['cr']} out={t['out']}")
PY
