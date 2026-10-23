# Monitor de Preços BF

Acompanhamento diário do preço de 18 produtos muito procurados na Black Friday, de 1º de outubro a 30 de novembro de 2026. O preço vem de posts públicos de ofertas no X, coletados via Buzzmonitor. O painel mostra como o preço de cada produto evolui em relação ao começo de outubro.

Painel: https://claude.ai/artifact/SfovXBwiovWXw3yYKW9qr6 (privado) e site público no Netlify, publicado a partir da pasta `site/` (configuração em `netlify.toml`).

## Estrutura

| Caminho | O que é |
|---|---|
| `scripts/products.json` | Produtos acompanhados: nome, categoria, termo de busca, regras de identificação do modelo e faixa de preço válida |
| `scripts/extract.py` | Lê os posts brutos em `raw/`, identifica o produto, extrai o preço "por" e o "de", limpa kits, acessórios, repetições e preços fora da curva |
| `scripts/build.py` | Calcula preço do dia, referência (1 a 15/10), variação, desconto anunciado, visão por categoria (atual e semanal) e visão por loja |
| `scripts/lojas.py` | Identifica a loja citada em cada post (posts que citam várias lojas ficam sem loja) |
| `scripts/render.py` + `scripts/template.html` | Gera `site/blackfraude.html` (Artifact) e `site/index.html` (Netlify) com os dados embutidos |
| `data/ofertas_brutas.json` | Histórico acumulado de todas as ofertas extraídas |
| `data/ofertas.json` | Ofertas depois da limpeza |
| `data/data.json` | Dados que alimentam o painel |
| `AGENTE.md` | Rotina diária da tarefa agendada |

## Portugal

Versão portuguesa focada em descontos anunciados (não em preço por modelo, porque em Portugal o mesmo modelo raramente aparece em vários dias): `paises/pt/` (extrator, cálculo e modelo), `data-pt/` (dados) e `site-pt/` (páginas). Painel: https://claude.ai/artifact/Bup8kdzynwaieUvnST3ddv. Para o Netlify, crie um segundo site a partir deste repositório com a pasta de publicação `site-pt`.

## Rodar localmente

```bash
python3 scripts/extract.py "raw/**/*"
python3 scripts/build.py
python3 scripts/render.py
```

A metodologia completa está na própria página, na seção "Metodologia".
