import json, os
from PIL import Image
BASE = os.path.dirname(os.path.abspath(__file__))
SPEC = json.load(open(os.path.join(BASE, '_spec.json')))
report = []
for folder, blk in SPEC.items():
    outdir = os.path.join(BASE, folder)
    images, missing = [], []
    for it in blk['items']:
        p = os.path.join(outdir, it['key'] + '.png')
        if not (os.path.exists(p) and os.path.getsize(p) > 5000):
            missing.append(it['key']); continue
        im = Image.open(p)
        if it.get('transparent'):
            im = im.convert('RGBA')
            bbox = im.getchannel('A').getbbox()
            if bbox and (bbox[2]-bbox[0]) * (bbox[3]-bbox[1]) > 1000:
                im = im.crop(bbox); im.save(p)
            im = Image.open(p)
        images.append({"key": it['key'], "file": it['key'] + '.png', "w": im.size[0], "h": im.size[1],
                       "prompt": it['prompt'], "용도": it['use']})
    json.dump({"code": blk['code'], "folder": folder, "images": images},
              open(os.path.join(outdir, 'manifest.json'), 'w'), ensure_ascii=False, indent=1)
    report.append((folder, blk['code'], len(images), missing))
for r in report:
    print(r[0], r[1], 'n=%d' % r[2], 'MISSING:' + ','.join(r[3]) if r[3] else '')
