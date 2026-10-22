import sys, os
from PIL import Image
seg, out, h = sys.argv[1], sys.argv[2], int(sys.argv[3])
offs = {}
for line in open(os.path.join(seg,'offsets.txt')):
    i, y = line.split(); offs[int(i)] = int(y)
idx = sorted(offs)
imgs = [Image.open(os.path.join(seg, f's{i}.png')).convert('RGB') for i in idx]
scale = imgs[0].width / 364 if imgs[0].width else 1
# use real css h -> px
pxh = imgs[0].height
sc = pxh / h
total_css = offs[idx[-1]] + h
canvas = Image.new('RGB', (imgs[0].width, int(round(total_css*sc))), 'white')
prev_end = 0  # css coord already pasted up to
for k, i in enumerate(idx):
    y = offs[i]
    src_top_css = max(0, prev_end - y)
    if src_top_css >= h: continue
    box = (0, int(round(src_top_css*sc)), imgs[k].width, pxh)
    part = imgs[k].crop(box)
    canvas.paste(part, (0, int(round((y+src_top_css)*sc))))
    prev_end = y + h
canvas.save(out)
print('stitched', canvas.size)
