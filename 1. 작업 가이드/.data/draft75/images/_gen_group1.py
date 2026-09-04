import json, os, sys, base64, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.abspath(__file__))
KEY = json.load(open(os.path.expanduser('~/.config/cdbd/credentials.json')))['openai_api_key']
SPEC = json.load(open(os.path.join(BASE, '_spec_group1.json')))
only = sys.argv[1:] if len(sys.argv) > 1 else list(SPEC.keys())
lock = threading.Lock()

def log(*a):
    with lock:
        print(*a, flush=True)

def gen(folder, item):
    outdir = os.path.join(BASE, folder)
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, item['key'] + '.png')
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        log('SKIP(exists)', folder, item['key'])
        return (folder, item, 'skip', None)
    body = {"model": "gpt-image-1", "prompt": item['prompt'], "size": item['size'],
            "n": 1, "quality": item.get('q', 'medium'), "output_format": "png"}
    if item.get('transparent'):
        body["background"] = "transparent"
    err = None
    for attempt in range(3):
        try:
            req = urllib.request.Request("https://api.openai.com/v1/images/generations",
                data=json.dumps(body).encode(),
                headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.loads(r.read())
            open(path, 'wb').write(base64.b64decode(d['data'][0]['b64_json']))
            log('OK', folder, item['key'], os.path.getsize(path))
            return (folder, item, 'ok', None)
        except urllib.error.HTTPError as e:
            err = '%s %s' % (e.code, e.read()[:300].decode('utf8', 'replace'))
        except Exception as e:
            err = repr(e)
        log('RETRY', folder, item['key'], 'attempt', attempt + 1, err[:200])
        time.sleep(5 + attempt * 10)
    log('FAIL', folder, item['key'], err[:300])
    return (folder, item, 'fail', err)

jobs = [(f, it) for f in only for it in SPEC[f]['items']]
results = []
with ThreadPoolExecutor(max_workers=5) as ex:
    futs = [ex.submit(gen, f, it) for f, it in jobs]
    for fu in as_completed(futs):
        results.append(fu.result())
json.dump([{'folder': f, 'key': i['key'], 'status': s, 'err': e} for f, i, s, e in results],
          open(os.path.join(BASE, '_result_%s.json' % ('_'.join(only) if len(only) < 4 else 'all')), 'w'),
          ensure_ascii=False, indent=1)
print('DONE', sum(1 for r in results if r[2] == 'fail'), 'failures of', len(results))
