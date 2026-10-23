"""Portugal: injeta o CSS do painel do Brasil e data-pt/data.json no modelo e gera site-pt/portugal.html (Artifact) e site-pt/index.html (Netlify)."""
import re,os
br=open('scripts/template.html').read()
css=br[br.index('<style>')+7:br.index('</style>')]
t=open('paises/pt/template_pt.html').read().replace('/*CSS*/',css)
t=t.replace('/*DATA*/',open('data-pt/data.json').read().replace('</','<\\/'))
os.makedirs('site-pt',exist_ok=True)
open('site-pt/portugal.html','w').write(t)
i=t.index('</style>')+len('</style>')
head=('<!doctype html>\n<html lang="pt-PT">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
      '<meta name="description" content="Descontos anunciados nas redes em Portugal até à Black Friday 2026.">\n'
      '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}</style>\n')
open('site-pt/index.html','w').write(head+t[:i]+'\n</head>\n<body>\n'+t[i:]+'\n</body>\n</html>\n')
