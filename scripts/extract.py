"""Extrai ofertas (produto, preço por, preço de, loja) de posts do Buzzmonitor."""
import json,re,sys,glob
from collections import defaultdict
NUM=r'(\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?|\d+(?:,\d{1,2})?)'
def num(s):
    s=s.replace('.','').replace(',','.')
    try: return float(s)
    except: return None
LOJAS=[('mercado livre','Mercado Livre'),('amazon','Amazon'),('shopee','Shopee'),('magalu','Magalu'),('magazine luiza','Magalu'),('casas bahia','Casas Bahia'),('kabum','KaBuM!'),('americanas','Americanas'),('ponto','Ponto'),('fast shop','Fast Shop'),('carrefour','Carrefour'),('aliexpress','AliExpress'),('extra','Extra'),('girafa','Girafa'),('beleza na web','Beleza na Web'),('sephora','Sephora'),('época','Época Cosméticos')]
def loja(t):
    tl=t.lower()
    for k,v in LOJAS:
        if k in tl: return v
    return None
def precos(t,lo,hi):
    """Retorna (por, de) ou None."""
    t=t.replace(' ',' ')
    # remove trechos que não são preço do produto
    clean=re.sub(r'\d+\s*x\s*(de\s*)?R?\$?\s*'+NUM,' ',t,flags=re.I)            # parcelas
    clean=re.sub(r'R\$\s*'+NUM+r'\s*(OFF|de desconto)',' ',clean,flags=re.I)     # cupons R$ X OFF
    clean=re.sub(r'(OFF|acima|compras|pedidos?|m[íi]nimo)\s*(em|de|acima de)?\s*R\$\s*'+NUM,' ',clean,flags=re.I)
    clean=re.sub(r'(economi\w*|desconto de)\s*:?\s*R\$\s*'+NUM,' ',clean,flags=re.I)
    de=None;por=None
    m=re.search(r'\bde\s*:?\s*~?\s*R?\$?\s*'+NUM+r'\s*~?\s*[|\-–,]?\s*(?:💥|💰|🤑|🔥|⚡|💸|💵|\*|\s)*\s*por',clean,re.I)
    if m: de=num(m.group(1))
    m=re.search(r'\bpor\s*:?\s*(?:apenas|só|somente)?\s*:?\s*R\$\s*'+NUM,clean,re.I)
    if m: por=num(m.group(1))
    if por is None:
        m=re.search(r'R\$\s*'+NUM+r'\s*(?:→|->|➡️?|para)\s*(?:apenas\s*)?R\$\s*'+NUM,clean,re.I)
        if m: de,por=num(m.group(1)),num(m.group(2))
    if por is None:
        vals=[num(x) for x in re.findall(r'R\$\s*'+NUM,clean)]
        vals=[v for v in vals if v and lo<=v<=hi]
        if vals:
            por=min(vals)
            if de is None:
                big=[v for v in vals if v>por]
                if big: de=max(big)
    if por is None or not(lo<=por<=hi): return None
    if de is not None and not(por<de<=por*4): de=None
    return por,de
KIT=re.compile(r'\bkit\b|\bcombo\b|\d\s*unidades',re.I)
# posts que comparam modelos ("S25 Ultra vs S26 Ultra") misturam preços de produtos diferentes
COMPARA=re.compile(r'\bvs\.?\s|\bversus\b|comparativo|qual vale mais|com troca|troca extra|na troca|trade.?in',re.I)  # inclui preços que dependem de entregar um aparelho usado
def extrair(posts,prods):
    out=[]
    comp=[(p,re.compile(p['inc'],re.I),re.compile(p['exc'],re.I)) for p in prods]
    for post in posts:
        t=post.get('content') or ''
        if t.startswith(('RT @','@')) or 'R$' not in t or 'http' not in t or COMPARA.search(t): continue
        for p,inc,exc in comp:
            m=inc.search(t)
            if not m: continue
            # exclusão olha só a linha/título do produto, onde o acessório apareceria
            janela=t[max(0,m.start()-60):m.end()+60]
            if exc.search(janela) or KIT.search(janela): continue
            r=precos(t,p['min'],p['max'])
            if not r: continue
            out.append({'produto':p['id'],'data':post['date'][:8],'hora':post['date'][8:12],'por':r[0],'de':r[1],
                        'loja':loja(t),'rede':post.get('service'),'autor':(post.get('author') or {}).get('login'),
                        'link':post.get('link'),'texto':re.sub(r'\s+',' ',t)[:280]})
    return out
if __name__=='__main__':
    from pool import load
    prods=json.load(open('scripts/products.json'))
    posts=load(sys.argv[1] if len(sys.argv)>1 else 'raw/**/*')
    of=extrair(posts,prods)
    # acumula com o histórico já coletado (data/ofertas_brutas.json)
    import os
    hist='data/ofertas_brutas.json'
    if os.path.exists(hist): of=json.load(open(hist))+of
    vistos=set(); uniq=[]
    for o in of:
        k=(o['produto'],o['link'])
        if k in vistos: continue
        vistos.add(k); uniq.append(o)
    of=uniq
    os.makedirs('data',exist_ok=True)
    json.dump(of,open(hist,'w'),ensure_ascii=False,indent=0)
    # dedupe: mesmo produto, dia, preço e loja (reposts entre perfis de cupons)
    seen=set();ded=[]
    for o in sorted(of,key=lambda o:(o['data'],o['hora'])):
        k=(o['produto'],o['data'],round(o['por']),o['loja'])
        if k in seen: continue
        seen.add(k);ded.append(o)
    # remove preços fora da curva (erro de extração, variante errada): fora de 0,6x a 1,6x a mediana do produto
    import statistics
    med={p['id']:statistics.median([o['por'] for o in ded if o['produto']==p['id']] or [0]) for p in prods}
    ded=[o for o in ded if 0.6*med[o['produto']]<=o['por']<=1.6*med[o['produto']]]
    json.dump(ded,open('data/ofertas.json','w'),ensure_ascii=False,indent=0)
    by=defaultdict(set);cnt=defaultdict(int)
    for o in ded: by[o['produto']].add(o['data']);cnt[o['produto']]+=1
    for p in prods: print(f"{p['id']:24s} ofertas={cnt[p['id']]:4d} dias={len(by[p['id']]):2d}")
