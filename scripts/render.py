"""Injeta data/data.json no template e gera:
- site/blackfraude.html: página para o Artifact (o Artifact adiciona o esqueleto HTML)
- site/index.html: documento HTML completo para o Netlify
"""
import json,sys
data=open('data/data.json').read().replace('</','<\\/')
corpo=open('scripts/template.html').read().replace('/*DATA*/',data)
open(sys.argv[1] if len(sys.argv)>1 else 'site/blackfraude.html','w').write(corpo)
desc='Acompanhamento diário do preço de produtos em posts de oferta até a Black Friday 2026.'
cabeca=('<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        f'<meta name="description" content="{desc}">\n<meta property="og:title" content="Monitor de Preços BF">\n'
        f'<meta property="og:description" content="{desc}">\n'
        '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}</style>\n')
# move <title>, metas, links e <style> do template para o <head>
i=corpo.index('</style>')+len('</style>')
open('site/index.html','w').write(cabeca+corpo[:i]+'\n</head>\n<body>\n'+corpo[i:]+'\n</body>\n</html>\n')
