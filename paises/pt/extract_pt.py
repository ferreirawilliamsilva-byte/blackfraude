"""Portugal: extrai ofertas com desconto anunciado de posts com preço em euros.
Diferente do Brasil, aqui não se acompanha o preço de um modelo exato:
cada oferta entra pela categoria e pelo desconto que o post anuncia."""
import json,re,sys,os
sys.path.insert(0,'scripts')
from pool import load

NUM=r'(\d{1,3}(?:[.\s]\d{3})*(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)'
def num(s):
    s=s.replace(' ','')
    if ',' in s: s=s.replace('.','').replace(',','.')          # 1.439,99
    elif re.fullmatch(r'\d{1,3}(\.\d{3})+',s): s=s.replace('.','')  # 1.439
    try: return float(s)
    except ValueError: return None
EUR=r'(?:'+NUM+r'\s?€|€\s?'+NUM+r')'
def eur(m): return num(m.group(1) or m.group(2))

CATS=[ # ordem importa: a primeira que casar define a categoria
 ('Áudio e relógios',r'airpods|auricular|auscultador|headphone|buds|coluna\s|\bjbl\b|smartwatch|smart watch|rel[óo]gio|apple\s*watch|galaxy\s*watch'),
 ('Beleza',r'perfume|eau de|secador|maquilhagem|skincare|alisador|escova de cabelo'),
 ('TVs',r'\bsmart\s*tv\b|\btv\b|televis|\boled\b|\bqled\b|mini\s?led'),
 ('Informática',r'kindle|e-?reader|port[áa]til|laptop|macbook|\bipad\b|tablet|\bpad\s*\d|monitor\b|\bssd\b|computador'),
 ('Telemóveis',r'telem[óo]vel|smartphone|iphone|galaxy\s*[asz]\d|redmi\s*note|xiaomi\s*\d|pixel\s*\d|vivo\s*v\d'),
 ('Consolas e jogos',r'\bps5\b|playstation|nintendo|switch\s*2|xbox'),
 ('Casa',r'air\s*fryer|airfryer|fritadeira|aspirador|m[áa]quina de (lavar|caf)|frigor[íi]fico|micro-?ondas|bimby|robot de cozinha|ar[\s-]condicionado|cafeteira'),
]
LOJAS={'Worten':r'worten','Fnac':r'\bfnac\b','Rádio Popular':r'r[áa]dio\s*popular','El Corte Inglés':r'corte\s*ingl','MediaMarkt':r'media\s*markt','Continente':r'continente','Amazon':r'amazon','PcDiga':r'pcdiga','Darty':r'darty','Auchan':r'auchan','Pingo Doce':r'pingo\s*doce','Lidl':r'\blidl\b','Primor':r'primor','Douglas':r'douglas','Wells':r'\bwells\b','Perfumes & Companhia':r'perfumes\s*(&|e)\s*companhia','Temu':r'\btemu\b','AliExpress':r'aliexpress','Leroy Merlin':r'leroy'}
SINAL_PT=re.compile(r'portugal|🇵🇹|\.pt\b|'+'|'.join(LOJAS.values())+r'|telem[óo]vel|ecr[ãa]|frigor[íi]fico|cup[ãa]o|portes|IVA|4gnews|pplware|leak|zwame|maisbarato',re.I)
BR=re.compile(r'R\$|reais|frete|mercado\s*livre|shopee|magalu|pix\b',re.I)

def desconto(t):
    """Desconto anunciado em %: explícito (-30%, 30% de desconto) ou calculado de antes/agora."""
    m=re.search(r'antes[:\s]*'+EUR+r'.{0,40}?(?:agora|por)[:\s]*'+EUR,t,re.I|re.S) or \
      re.search(r'❌\s*'+EUR+r'.{0,20}?✅\s*'+EUR,t,re.S) or \
      re.search(r'\bde\s*'+EUR+r'\s*(?:para|por|→|->)\s*'+EUR,t,re.I)
    if m:
        g=[x for x in m.groups() if x]
        if len(g)>=2:
            a,b=num(g[0]),num(g[1])
            if a and b and 0<b<a<=b*5: return round((a-b)/a*100),a,b
    m=re.search(r'-\s?(\d{1,2})\s?%|(\d{1,2})\s?%\s*(?:de\s*)?(?:desconto|off)',t,re.I)
    if m:
        p=int(m.group(1) or m.group(2))
        if 3<=p<=90:
            pr=[eur(x) for x in re.finditer(EUR,t)]
            pr=[x for x in pr if x]
            return p,None,(min(pr) if pr else None)
    return None

ACESS=re.compile(r'powerbank|power bank|capa|pel[íi]cula|carregador|cabo usb|suporte',re.I)
def extrair(posts):
    out=[]
    for p in posts:
        t=(p.get('content') or '').strip()
        if not t or t.startswith('RT @') or '€' not in t or BR.search(t): continue
        if p.get('language') not in ('pt',None): continue
        if not SINAL_PT.search(t): continue
        d=desconto(t)
        if not d: continue
        tl=t.lower()
        cat=next((c for c,rx in CATS if re.search(rx,tl) and not (c=='Telemóveis' and ACESS.search(tl))),None)  # acessórios não contam como telemóvel
        if cat is None: continue  # fora das categorias acompanhadas (seguros, combustível, bicicletas...)
        lojas=[l for l,rx in LOJAS.items() if re.search(rx,tl)]
        out.append({'data':p['date'][:8],'hora':p['date'][8:12],'categoria':cat,'desconto':d[0],'antes':d[1],'agora':d[2],
                    'loja':lojas[0] if len(lojas)==1 else None,'rede':p.get('service'),'link':p.get('link'),
                    'titulo':re.sub(r'\s+',' ',t)[:140],'texto':re.sub(r'\s+',' ',t)[:300],'autor':(p.get('author') or {}).get('login'),'fonte':'4gnews' if '4gnews' in tl else ('maisbarato' if 'maisbarato' in tl else (p.get('author') or {}).get('login'))})
    return out

if __name__=='__main__':
    posts=load(sys.argv[1] if len(sys.argv)>1 else 'raw-pt/**/*')
    of=extrair(posts)
    hist='data-pt/ofertas.json'; os.makedirs('data-pt',exist_ok=True)
    if os.path.exists(hist): of=json.load(open(hist))+of
    vistos=set(); uniq=[]
    for o in sorted(of,key=lambda o:o['data']+o['hora']):
        k=o['link'] or o['texto']; k2=(o['titulo'][:60],o['data'],o['desconto'])
        if k in vistos or k2 in vistos: continue
        vistos.add(k); vistos.add(k2); uniq.append(o)
    json.dump(uniq,open(hist,'w'),ensure_ascii=False,indent=0)
    from collections import Counter
    print('ofertas PT com desconto:',len(uniq))
    print(Counter(o['categoria'] for o in uniq).most_common())
    print(Counter(o['loja'] for o in uniq).most_common(10))
    print(Counter(o['rede'] for o in uniq).most_common())
