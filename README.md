# BlackFraude

Acompanhamento diário do preço de 18 produtos muito procurados na Black Friday, de 1º de outubro a 30 de novembro de 2026. O preço vem de posts públicos de ofertas no X, coletados via Buzzmonitor. A pergunta que o painel responde: o desconto da Black Friday é real, ou o preço subiu antes para o "desconto" parecer maior?

Painel: https://claude.ai/artifact/SfovXBwiovWXw3yYKW9qr6 (privado) e site público no Netlify, publicado a partir da pasta `site/` (configuração em `netlify.toml`).

## Estrutura

| Caminho | O que é |
|---|---|
| `scripts/products.json` | Produtos acompanhados: nome, categoria, termo de busca, regras de identificação do modelo e faixa de preço válida |
| `scripts/extract.py` | Lê os posts brutos em `raw/`, identifica o produto, extrai o preço "por" e o "de", limpa kits, acessórios, repetições e preços fora da curva |
| `scripts/build.py` | Calcula preço do dia, referência (1 a 15/10), variação, desconto prometido e visão por categoria |
| `scripts/render.py` + `scripts/template.html` | Gera `site/blackfraude.html` (Artifact) e `site/index.html` (Netlify) com os dados embutidos |
| `data/ofertas_brutas.json` | Histórico acumulado de todas as ofertas extraídas |
| `data/ofertas.json` | Ofertas depois da limpeza |
| `data/data.json` | Dados que alimentam o painel |
| `AGENTE.md` | Rotina diária da tarefa agendada |

## Rodar localmente

```bash
python3 scripts/extract.py "raw/**/*"
python3 scripts/build.py
python3 scripts/render.py
```

A metodologia completa está na própria página, na seção "Metodologia".
