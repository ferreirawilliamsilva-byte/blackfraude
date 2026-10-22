import json,glob,os
def _parse(raw):
    raw=raw.strip()
    if raw.startswith('['):  # formato persistido: [{"type":"text","text":"{...}"}]
        raw=json.loads(raw)[0]['text']
    return json.loads(raw[raw.find('{'):])
def load(globpat):
    seen={}
    for pat in globpat.split(','):
        for f in sorted(x for x in glob.glob(pat,recursive=True) if os.path.isfile(x)):
            for p in _parse(open(f).read())['data']:
                k=p.get('link') or (p['date']+(p.get('content') or '')[:80])
                seen[k]=p
    return list(seen.values())
