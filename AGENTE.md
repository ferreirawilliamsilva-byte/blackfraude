# Rotina diária do agente BlackFraude

Este arquivo é a instrução da tarefa agendada que roda todo dia às 8h (horário de Brasília) de 23/10 a 01/12/2026. Siga os passos na ordem. Se um passo falhar, pare e diga no resumo final exatamente qual passo falhou e por quê.

Painel publicado (Artifact): https://claude.ai/artifact/SfovXBwiovWXw3yYKW9qr6

## 0. Antes de começar

- Se a data de hoje for depois de 01/12/2026, não faça nada e encerre dizendo que o acompanhamento terminou.
- Trabalhe na raiz deste repositório, na branch `main`. Faça `git pull origin main` antes de tudo.

## 1. Descobrir quais dias coletar

Leia `data/data.json`, campo `coleta_ate` (último dia com dados). Colete **todos os dias** de `coleta_ate + 1` até **ontem**. Normalmente é um dia só, mas se uma execução anterior falhou, recupere os dias que faltam: a busca do Buzzmonitor é histórica.

## 2. Buscar os posts no Buzzmonitor

Para cada dia a coletar e para cada produto de `scripts/products.json`, chame a ferramenta `search_historical_posts` do MCP do Buzzmonitor (Buzz MCP Trends) com:

- `query`: o campo `query` do produto, exatamente como está (sem aspas, sem AND)
- `since`: `AAAAMMDD000000` e `until`: `AAAAMMDD235959` do dia
- `service`: `["twitter"]`
- `fields`: `["link"]`

Produtos com a mesma `query` (por exemplo, as duas air fryers) precisam de uma busca só por dia.

Salve a resposta **completa e sem alterações** de cada busca em `raw/AAAAMMDD/<query-sem-espacos>.json`:

- Quando a ferramenta salvar o resultado num arquivo (resposta grande), copie esse arquivo para o caminho acima.
- Quando o resultado vier direto na conversa (resposta pequena), grave o JSON recebido nesse caminho.
- Não invente, não edite e não resuma posts. Se uma busca falhar, tente de novo uma vez. Se falhar de novo, registre no resumo e siga.

## 3. Processar

```bash
python3 scripts/extract.py "raw/**/*"     # extrai preços e acumula em data/ofertas_brutas.json e data/ofertas.json
python3 scripts/build.py                  # recalcula variações, categorias e data/data.json (hora atual de Brasília)
python3 scripts/render.py                 # gera site/blackfraude.html (Artifact) e site/index.html (Netlify)
```

Confira na saída do `build.py` que `coleta até` passou a ser ontem e que o número de ofertas não diminuiu. Se diminuiu, algo deu errado: não publique.

## 4. Salvar no repositório

```bash
git add data site scripts
git commit -m "Coleta diária: dados até AAAA-MM-DD"
git push origin main
```

A pasta `raw/` fica fora do git (está no `.gitignore`). O push em `main` também atualiza o site no Netlify, que publica a pasta `site/` automaticamente.

## 5. Atualizar o painel

Republique `site/blackfraude.html` no **mesmo** Artifact. Primeiro leia o artifact com a ferramenta Artifact (`action: "read"`, `url` acima). Depois publique com `url` = o link acima e `file_path` = `site/blackfraude.html`. Nunca publique sem `url`, porque isso criaria um link novo.

## 6. Resumo final

Termine com um resumo curto: dias coletados, quantas ofertas novas, produtos que mais mudaram, e qualquer busca que falhou. Não cite nomes de lojas no resumo.

## Regras do painel

- O painel não cita as lojas que vendem os produtos. O campo `loja` só existe em `data/ofertas_brutas.json` e nunca vai para `data/data.json`.
- Não altere a lista de produtos, os limites de preço ou a metodologia sem pedido explícito do responsável pelo projeto.
