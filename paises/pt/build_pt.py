"""Portugal: gera data-pt/data.json (descontos anunciados por categoria, semana, loja e fonte)."""
import json,statistics as st,datetime as dt,sys
from collections import defaultdict,Counter
INICIO=dt.date(2026,10,1); BF=dt.date(2026,11,27); FIM=dt.date(2026,11,30)
MIN_CAT=10   # categorias com menos ofertas no período ficam como "poucos dados"
O=json.load(open('data-pt/ofertas.json'))
lisboa=dt.timezone(dt.timedelta(hours=1 if dt.date.today()>=dt.date(2026,10,25) else 0))  # WEST até 25/10, WET depois
agora=sys.argv[1] if len(sys.argv)>1 else dt.datetime.now(lisboa).isoformat(timespec='seconds')
d=lambda s:dt.date(int(s[:4]),int(s[4:6]),int(s[6:8]))
seg=lambda x:x-dt.timedelta(days=x.weekday())
ult=max(d(o['data']) for o in O)
semanas=sorted({seg(d(o['data'])) for o in O})
med=lambda v:round(st.median(v)) if v else None
cats=[]
porcat=defaultdict(list)
for o in O: porcat[o['categoria']].append(o)
for c,os_ in porcat.items():
    ws=[]
    for w in semanas:
        v=[o['desconto'] for o in os_ if seg(d(o['data']))==w]
        ws.append({'inicio':w.isoformat(),'n':len(v),'desconto':med(v)})
    melhor=max(os_,key=lambda o:o['desconto'])
    cats.append({'categoria':c,'n':len(os_),'desconto':med([o['desconto'] for o in os_]),'max':melhor['desconto'],
                 'poucos_dados':len(os_)<MIN_CAT,'semanas':ws,
                 'melhor':{k:melhor[k] for k in ('titulo','desconto','antes','agora','link','data')}})
cats.sort(key=lambda c:(c['poucos_dados'],-(c['desconto'] or 0)))
lojas=[]
pl=defaultdict(list)
for o in O:
    if o['loja']: pl[o['loja']].append(o['desconto'])
for l,v in pl.items():
    if len(v)>=3: lojas.append({'loja':l,'n':len(v),'desconto':med(v),'max':max(v)})
lojas.sort(key=lambda x:-x['n'])
fontes=Counter(o['fonte'] if o['fonte'] in ('maisbarato','4gnews') else 'outras' for o in O)
NOMES={'maisbarato':'Perfil de Instagram #maisbarato','4gnews':'Site 4gnews','outras':'Outras fontes'}
fontes=[{'fonte':NOMES[k],'n':v,'pct':round(v/len(O)*100)} for k,v in fontes.most_common()]
dias=Counter(o['data'] for o in O)
volume=[]
x=INICIO
while x<=ult:
    k=x.strftime('%Y%m%d'); volume.append({'d':k,'n':dias.get(k,0)}); x+=dt.timedelta(days=1)
import re
def limpa(t):
    """Tira créditos de imagem e etiquetas do início do título."""
    t=re.sub(r'^\s*(Cr[ée]dito:\s*\([^)]*\)|Foto de\s+[A-ZÀ-Ú][\w-]+(\s+[A-ZÀ-Ú][\w-]+)?|Imagem gerada por IA\s*\|\s*\w+|Via\s+\w+)\s*','',t)
    t=re.sub(r'^[^\w(]*(OFERTA DO DIA|PROMO[ÇC][ÃA]O|DICA)\s*','',t,flags=re.I)
    return t.strip()
for o in O: o['titulo']=limpa(o['titulo'])
recentes=[o for o in O if d(o['data'])>ult-dt.timedelta(days=13)]
top=[];vist=set()
for o in sorted(recentes,key=lambda o:-o['desconto']):
    k=re.sub(r'\W+',' ',o['titulo'].lower())[:40]
    if k in vist: continue
    vist.add(k);top.append(o)
    if len(top)==10: break
ws_last=semanas[-1]; ws_prev=semanas[-2] if len(semanas)>1 else None
def semana_med(w): v=[o['desconto'] for o in O if seg(d(o['data']))==w]; return med(v),len(v)
data={'pais':'Portugal','atualizado_em':agora,'coleta_ate':ult.isoformat(),'inicio':INICIO.isoformat(),'black_friday':BF.isoformat(),'fim':FIM.isoformat(),
      'total_ofertas':len(O),'semanas':[w.isoformat() for w in semanas],'categorias':cats,'lojas':lojas,'fontes':fontes,'volume':volume,
      'top':[{k:o[k] for k in ('titulo','categoria','desconto','antes','agora','link','data')} for o in top],
      'semana_atual':dict(zip(('desconto','n'),semana_med(ws_last)),inicio=ws_last.isoformat()),
      'semana_anterior':dict(zip(('desconto','n'),semana_med(ws_prev)),inicio=ws_prev.isoformat()) if ws_prev else None,
      'feed':[{k:o[k] for k in ('titulo','desconto','link','data','hora')} for o in sorted(O,key=lambda o:o['data']+o['hora'],reverse=True)[:25]]}
json.dump(data,open('data-pt/data.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(O),'ofertas | coleta até',ult,'| semana atual',data['semana_atual'],'| anterior',data['semana_anterior'])
for c in cats: print(f"  {c['categoria']:18s} n={c['n']:3d} desconto={c['desconto']} max={c['max']} poucos={c['poucos_dados']}")
print('  lojas',[(l['loja'],l['n'],l['desconto']) for l in lojas]); print('  fontes',fontes)
