import re, json, sys, os
sys.path.insert(0, '/Users/mustard/Documents/GitHub/design/cdbd-templates/1. 작업 가이드/도구')
import dom2fig

VIDS = ['1a','2b','3c','4d','5e','5f','5g']
for vid in VIDS:
    h = open(f'/tmp/variant-{vid}.html', encoding='utf-8').read()
    scr = re.search(r'class="scr"[^>]*style="([^"]*)"', h)
    bg  = re.search(r'background:\s*([^;"]+)', scr.group(1)).group(1).strip()
    lab = re.findall(r"font:600 16px/1\.3 'Pretendard';color:[^\"]*\">([^<]*)<", h)
    name = f"{vid} · {lab[0] if lab else ''}".strip()

    marks = [(m.start(), m.end(), m.group(1).strip())
             for m in re.finditer(r'<!--\s*카드:\s*(.*?)\s*-->', h)]
    cards = []
    for i, (s, e, typ) in enumerate(marks):
        end = marks[i+1][0] if i+1 < len(marks) else len(h)
        cards.append({'type': typ, 'tree': dom2fig.build(h[e:end], 390)})

    D = {'theme': {'name': name, 'bg': bg}, 'cards': cards}
    p = f'/tmp/D-{vid}.json'
    json.dump(D, open(p,'w'), ensure_ascii=False, separators=(',',':'))
    print(f'{vid}  카드 {len(cards):2d}  {os.path.getsize(p)/1024:5.1f}KB  bg={bg}  {name}')
