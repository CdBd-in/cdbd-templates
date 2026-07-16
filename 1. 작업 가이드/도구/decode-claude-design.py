#!/usr/bin/env python3
"""claude.ai/design 'standalone HTML' → 실제 디자인 HTML 추출.
사용: python3 decode-claude-design.py "~/Downloads/X (standalone).html" out.html
원리: standalone은 번들러 껍데기. 실제 디자인 HTML은 <script type="__bundler/template">
      안에 JSON 문자열로 escape되어 있음 (보통 파일에서 2번째로 긴 줄)."""
import json, sys
src, dst = sys.argv[1], sys.argv[2]
lines = open(src, encoding='utf-8').read().split('\n')
for idx in sorted(range(len(lines)), key=lambda i: len(lines[i]), reverse=True)[:6]:
    s = lines[idx].strip()
    if s.startswith('"<!DOCTYPE') or ('DOCTYPE' in s[:220] and '\\u002F' in s):
        end = s.rfind('</script>')
        if end != -1: s = s[:end].rstrip()
        try:
            html = json.loads(s)
            open(dst, 'w', encoding='utf-8').write(html)
            print(f'decoded line {idx} -> {dst} ({len(html)} chars)'); break
        except Exception as e:
            print('fail', idx, str(e)[:60])
