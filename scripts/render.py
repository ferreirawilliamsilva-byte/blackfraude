"""Injeta data.json no template e gera blackfraude.html."""
import json,sys
data=open('data/data.json').read().replace('</','<\\/')
html=open('scripts/template.html').read().replace('/*DATA*/',data)
open(sys.argv[1] if len(sys.argv)>1 else 'site/blackfraude.html','w').write(html)
