"""Gera data.json do painel BlackFraude a partir de ofertas.json."""
import json,statistics as st,datetime as dt,sys
from collections import defaultdict
INICIO=dt.date(2026,10,1); BF=dt.date(2026,11,27); FIM=dt.date(2026,11,30)
REF_ATE=dt.date(2026,10,15)
prods=json.load(open('scripts/products.json'))
ofertas=json.load(open('data/ofertas.json'))
agora=sys.argv[1] if len(sys.argv)>1 else dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).strftime('%Y-%m-%dT%H:%M:00-03:00')
def d(s): return dt.date(int(s[:4]),int(s[4:6]),int(s[6:8]))
by=defaultdict(lambda: defaultdict(list))
for o in ofertas: by[o['produto']][o['data']].append(o)
ultimo_dia=max(d(o['data']) for o in ofertas)
out=[]
for p in prods:
    dias=by[p['id']]
    serie=[]
    for k in sorted(dias):
        v=[o['por'] for o in dias[k]]
        serie.append({'d':k,'med':round(st.median(v),2),'min':round(min(v),2),'n':len(v)})
    ref_vals=[s['min'] for s in serie if d(s['d'])<=REF_ATE]
    if len(ref_vals)<3: continue
    ref=st.median(ref_vals)
    # preço atual: mediana dos últimos 3 dias com dado
    ult=serie[-3:]; atual=st.median([s['min'] for s in ult])
    var=(atual-ref)/ref*100
    # variação na semana: compara com os 3 dias anteriores a 7 dias atrás
    sem=[s['min'] for s in serie if d(s['d'])<=ultimo_dia-dt.timedelta(days=7)][-3:]
    var7=((atual-st.median(sem))/st.median(sem)*100) if sem else None
    for s in serie: s['var']=round((s['min']-ref)/ref*100,1)
    des=[(o['de']-o['por'])/o['de']*100 for k in dias for o in dias[k] if o['de']]
    anunciado=st.median(des) if des else None
    melhor=min((o for k in dias for o in dias[k]),key=lambda o:o['por'])
    recentes=sorted((o for k in dias for o in dias[k]),key=lambda o:o['data']+o['hora'],reverse=True)[:6]
    if var>=5: status='subiu'
    elif var<=-5: status='caiu'
    else: status='estavel'
    out.append({'id':p['id'],'nome':p['nome'],'categoria':p['categoria'],'ref':round(ref,2),'atual':round(atual,2),
        'var':round(var,1),'var7':None if var7 is None else round(var7,1),'status':status,
        'desconto_anunciado':None if anunciado is None else round(anunciado),
        'melhor':{'preco':melhor['por'],'data':melhor['data']},
        'dias_com_preco':len(serie),'poucos_dados':len(serie)<12,'ofertas':sum(s['n'] for s in serie),'serie':serie,
        'recentes':[{k:o[k] for k in ('data','hora','por','de','link')} for o in recentes]})
feed=sorted(({**{k:o[k] for k in ('data','hora','por','link')},'produto':o['produto']} for o in ofertas if any(x['id']==o['produto'] for x in out)),
            key=lambda o:o['data']+o['hora'],reverse=True)[:30]
# visão consolidada por categoria: mediana da variação dos produtos da categoria
cats=defaultdict(list)
for x in out: cats[x['categoria']].append(x)
categorias=[]
for c,xs in cats.items():
    categorias.append({'categoria':c,'var':round(st.median([x['var'] for x in xs]),1),
        'produtos':[{'id':x['id'],'nome':x['nome'],'var':x['var']} for x in sorted(xs,key=lambda x:x['var'])],
        'subiu':sum(x['status']=='subiu' for x in xs),'caiu':sum(x['status']=='caiu' for x in xs),'estavel':sum(x['status']=='estavel' for x in xs)})
categorias.sort(key=lambda c:-c['var'])
data={'categorias':categorias,'atualizado_em':agora,'coleta_ate':ultimo_dia.isoformat(),'inicio':INICIO.isoformat(),'black_friday':BF.isoformat(),'fim':FIM.isoformat(),
      'referencia':'mediana dos preços de 01 a 15/10','total_ofertas':sum(x['ofertas'] for x in out),'produtos':out,'feed':feed}
json.dump(data,open('data/data.json','w'),ensure_ascii=False,separators=(',',':'))
for x in sorted(out,key=lambda x:x['var']): print(f"{x['nome'][:34]:34s} ref={x['ref']:8.0f} atual={x['atual']:8.0f} var={x['var']:+6.1f}% sem={x['var7']} anunc={x['desconto_anunciado']} dias={x['dias_com_preco']}")
print(len(out),'produtos', data['total_ofertas'],'ofertas', 'coleta até',data['coleta_ate'])
