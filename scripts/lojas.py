"""Identifica a loja citada num post de oferta. Retorna None quando o post não cita loja ou cita várias."""
import re
LOJAS={
 'Mercado Livre':r'mercado\s*liv|mercadolivre|\bmeli\b|\bml\b',
 'Amazon':r'amazon',
 'Shopee':r'shopee',
 'Magalu':r'magalu|magazine\s*luiza|magazine\s*voc',
 'Casas Bahia':r'casas\s*bahia',
 'KaBuM!':r'kabum',
 'Americanas':r'americanas',
 'Fast Shop':r'fast\s*shop',
 'Carrefour':r'carrefour',
 'AliExpress':r'aliexpress',
 'Girafa':r'girafa',
 'Sephora':r'sephora',
 'Beleza na Web':r'beleza\s*na\s*web',
 'Época Cosméticos':r'época\s*cosm',
}
_NOMES=r'(?:shopee|amazon|mercado\s*livre|magalu)'
# listas genéricas de rodapé ("na Shopee, Amazon e Mercado Livre - Use o Cupom") não indicam onde está a oferta
_RODAPE=re.compile(_NOMES+r'(?:\s*,\s*'+_NOMES+r')*\s*(?:,|e)\s*'+_NOMES,re.I)
def loja(texto):
    t=_RODAPE.sub(' ',texto.lower())
    hits=[k for k,r in LOJAS.items() if re.search(r,t)]
    return hits[0] if len(hits)==1 else None
