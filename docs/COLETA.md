# Monitor de Preços BF: como os dados são coletados

Este documento descreve a coleta dos dois painéis: **Brasil** (`site/blackfraude.html`) e **Portugal** (`site-pt/portugal.html`). Todos os dados vêm da ferramenta `search_historical_posts` do MCP **Buzzmonitor Trends**, que faz busca histórica em posts públicos. Ele não usa uma conta ou projeto próprio do Buzzmonitor.

Situação em 04/11/2026, com dados até 03/11.

---

## Regras comuns aos dois painéis

| Item | Como funciona |
|---|---|
| Ferramenta | `search_historical_posts` (Buzzmonitor Trends) |
| Período do acompanhamento | 1º/10 a 30/11/2026 (Black Friday em 27/11) |
| Frequência | Uma coleta por dia, por volta das 8h no horário de Brasília (tarefa agendada) |
| Janela de cada coleta | De `coleta_ate − 4 dias` até ontem. Os posts chegam ao Buzzmonitor com 1 a 3 dias de atraso, então os últimos dias são buscados de novo para ficarem completos. Ofertas repetidas são descartadas pelo link. |
| Datas | Os posts vêm em horário UTC. O dia de hoje fica sempre de fora porque ainda está incompleto. |
| Uma busca por rede | Na ordenação padrão, a ferramenta aplica só a primeira rede da lista. Por isso há uma busca separada para cada rede. |
| Limite por busca | 5.000 posts. Quando uma busca chega ao limite, posts mais antigos ou com menos engajamento podem ficar de fora. |
| Arquivos brutos | Cada resposta é salva sem alterações em `raw/AAAAMMDD/` (Brasil) ou `raw-pt/AAAAMMDD/` (Portugal). Essas pastas ficam fora do git. |

---

## Painel Brasil: Monitor de Preços BF

**O que mede:** a variação do preço de 18 modelos exatos de produto em relação ao começo de outubro.

### Parâmetros das buscas

- `service`: `["twitter"]` (só o X)
- `since` / `until`: janela da coleta, por exemplo `20261029000000` a `20261103235959`
- `fields`: `["link", "imagem", "ids", "marca", "tipo", "idioma", "categorias", "metricas"]`
- `language`: não usado, o padrão é todos os idiomas. O português e o preço em R$ são garantidos depois, pelo leitor de preços.
- Uma busca por termo, cobrindo a janela toda. As duas air fryers usam termos diferentes, então são buscas separadas.

### Termos de busca (`query`) e produtos

As queries ficam em `scripts/products.json`. Depois da busca, cada post só conta para o produto se passar por um filtro de modelo (`inc`/`exc`) e por uma faixa de preço plausível (mínimo e máximo, em R$).

| # | `query` | Produto acompanhado | Categoria | Faixa aceita (R$) |
|---|---|---|---|---|
| 1 | `iphone 17` | iPhone 17 256GB | Celulares | 4.500 – 9.500 |
| 2 | `galaxy s26` | Galaxy S26 Ultra 256GB | Celulares | 5.000 – 12.000 |
| 3 | `galaxy a37` | Galaxy A37 128GB | Celulares | 1.100 – 3.200 |
| 4 | `ps5 slim` | PS5 Slim Digital | Games | 2.900 – 5.500 |
| 5 | `nintendo switch 2` | Nintendo Switch 2 | Games | 2.800 – 5.600 |
| 6 | `nintendo switch oled` | Nintendo Switch OLED | Games | 1.700 – 3.300 |
| 7 | `philco roku` | Smart TV Philco 43" Roku | TVs | 900 – 2.600 |
| 8 | `acer nitro` | Notebook Gamer Acer Nitro V15 i5 | Informática | 3.000 – 6.500 |
| 9 | `ipad` | iPad 11 (A16) 128GB | Informática | 2.000 – 4.200 |
| 10 | `apple watch series 11` | Apple Watch Series 11 GPS 42mm | Áudio e relógios | 2.300 – 5.500 |
| 11 | `airpods` | AirPods 4 | Áudio e relógios | 700 – 1.500 |
| 12 | `jbl flip 7` | JBL Flip 7 | Áudio e relógios | 450 – 1.200 |
| 13 | `air fryer philco` | Air Fryer Philco 6,5L Visor Glass | Casa | 250 – 750 |
| 14 | `air fryer mondial` | Air Fryer Mondial Dual 8L | Casa | 300 – 900 |
| 15 | `ar condicionado` | Ar-condicionado Philco 9.000 BTUs Inverter | Casa | 1.400 – 3.500 |
| 16 | `lavadora OR máquina de lavar` | Lavadora Electrolux 14,5kg Jet&Clean | Casa | 1.300 – 3.800 |
| 17 | `club de nuit` | Perfume Club de Nuit Intense 105ml | Beleza | 110 – 330 |
| 18 | `la vie est belle` | Perfume La Vie Est Belle EDP 30ml | Beleza | 220 – 600 |

### Do post ao preço

1. **Leitura:** o leitor identifica o modelo no texto e extrai o preço "por". Parcelas, valor de cupom ("R$ 30 OFF") e economia anunciada são ignorados.
2. **Limpeza:** são descartados kits e combos, acessórios (capa, película, cabo), usados e recondicionados, retuítes, posts repetidos com o mesmo preço no mesmo dia, posts comparativos, preços com troca de aparelho e preços fora da curva (abaixo de 60% ou acima de 160% do preço típico).
3. **Cálculos:**
   - Preço do dia: o menor preço anunciado.
   - Referência: mediana de 1º a 15/10.
   - Preço agora: mediana dos 3 últimos dias com preço.
   - Variação: (agora − referência) ÷ referência.
4. **Lojas:** identificadas pelo nome citado no post e mostradas só de forma agregada, na seção "Por loja".

**Volume até agora:** 1.206 ofertas válidas (1º/10 a 03/11).

**Pontos de atenção:**
- A busca `nintendo switch 2` tem batido no limite de 5.000 posts.
- A busca `apple watch series 11` passou vários dias seguidos sem nenhum post.

---

## Painel Portugal: Monitor de Descontos BF Portugal

**O que mede:** o **desconto anunciado** por categoria. Não acompanha o preço de um modelo exato, porque em Portugal o mesmo modelo raramente aparece em vários dias.

### Parâmetros das buscas de ofertas (7 por dia)

- `language`: `["pt"]` em todas
- `since` / `until`: janela da coleta, igual à do Brasil
- `fields`: `["link", "imagem", "ids", "marca", "tipo", "idioma", "categorias", "metricas"]`

| # | `service` | `query` | Para que serve |
|---|---|---|---|
| 1 | instagram | `smart tv OR televisão OR tv oled OR tv qled OR telemóvel OR smartphone OR iphone OR galaxy OR xiaomi` | TVs e telemóveis |
| 2 | instagram | `ps5 OR playstation OR nintendo switch OR xbox OR portátil OR ipad OR tablet OR monitor OR macbook` | Consolas e informática |
| 3 | instagram | `air fryer OR airfryer OR fritadeira OR aspirador OR máquina de lavar OR frigorífico OR bimby OR perfume OR secador` | Casa e beleza |
| 4 | news | `desconto OR descontos OR promoção OR promoções OR cupão OR "antes" OR "agora"` | Sites de notícias e de ofertas |
| 5 | facebook | `desconto OR descontos OR promoção OR promoções OR cupão OR worten OR fnac` | Páginas de ofertas |
| 6 | twitter | `desconto OR promoção OR cupão OR worten OR fnac OR "rádio popular" OR continente` | X |
| 7 | news | `4gnews` | Fonte 4gnews (desde 20/10) |

A busca 7 é separada porque a busca 4 bate quase sempre no limite de 5.000 posts e deixava de fora o 4gnews, uma das duas maiores fontes. A busca 4, apesar de ser por notícias, também devolve posts de Instagram, YouTube e Facebook.

### Do post à oferta

1. **Filtro de Portugal:** só entram posts em português com preço em euros e com sinais de Portugal (lojas, termos ou domínios portugueses).
2. **Desconto:** é usado o percentual explícito ("−30%", "30% de desconto") ou o cálculo a partir de "antes" e "agora".
3. **Categorias:** telemóveis, TVs, informática, áudio e relógios, consolas e jogos, casa e beleza. Seguros, combustível e viagens são descartados.
4. **Desconto típico:** a mediana dos descontos. Categorias com menos de 10 ofertas aparecem como "poucos dados".

**Volume até agora:** 110 ofertas (1º/10 a 03/11). Duas fontes concentram cerca de 87% delas: o site 4gnews (52%) e o perfil de Instagram #maisbarato (35%).

### Seção "Consumidores" (depoimentos)

É um retrato feito uma única vez, em 04/11, cobrindo 1º/10 a 03/11. A rotina diária não o atualiza. Os dados ficam em `data-pt/depoimentos.json`.

**Buscas extras,** além dos arquivos das 7 buscas diárias:

| `service` | `query` | `language` | Janela |
|---|---|---|---|
| twitter | `black friday OR blackfriday` | pt | 01/10 a 03/11 |
| facebook | `black friday OR blackfriday` | pt | 01/10 a 03/11 |
| instagram | `black friday OR blackfriday` | pt | 01/10 a 03/11 |
| reddit | `black friday OR blackfriday` | pt | 01/10 a 03/11 |

`fields`: `["link", "ids", "tipo", "idioma", "metricas"]`. A busca no Reddit não trouxe nenhum post do Reddit: a ferramenta devolveu posts de Instagram, YouTube e Facebook.

**Recorte regional por negativação** (skill `recorte-regional-por-negativacao`): não se tenta provar que um post é de Portugal. Exclui-se o que tem sinal forte de outro país e mantém-se o ambíguo.

| Etapa | Posts |
|---|---|
| Coletados (todas as respostas somadas) | 218.184 |
| Únicos após deduplicação | 74.414 |
| Excluídos por sinal de outro país | 51.698 (69,5%): Brasil 51.428 · PALOP 268 · Espanha 114 |
| Compatíveis com Portugal | 22.716 |
| Com sinal claro de Portugal (ancorados) | 1.938 |
| Ancorados, de pessoas e sobre consumo | 347 |
| Sem marcas de anúncio | 79 |
| **Depoimentos após leitura um a um** | **30** |

- **Sinais de outro país:** Brasil (R$, "você", "cupom", Mercado Livre, Shopee, cidades e bancos brasileiros), países africanos de língua portuguesa (Luanda, kwanza, Maputo) e Espanha.
- **Sinais claros de Portugal:** cidades portuguesas; lojas como Continente, Pingo Doce, Worten e Rádio Popular; MB Way e Multibanco; termos como "telemóvel" e "pequeno-almoço"; a construção "estou a fazer".
- **Critério de depoimento:** autor pessoa, ou seja, não é página, tem até 20 mil seguidores e não é notícia, blog nem YouTube. O post fala de consumo e não traz preço, link, código ou chamada de compra.
- **Correções feitas no dicionário:** "meo" (aparecia como erro de digitação de "meu") e "braga"/"guimaraes" (apareciam como sobrenome e em código de cupão) passaram a exigir contexto.
- **Limitações:**
  - 29 dos 30 depoimentos são do X.
  - O tema "boicote ao Continente e à Galp" (12 posts) vem quase todo de uma única conversa, em 18–19/10.
  - Os 20.778 posts compatíveis mas ambíguos não foram usados.

---

## O que não está documentado com precisão

As coletas iniciais (Brasil: `raw/coleta-inicial`, 39 arquivos; Portugal: `raw-pt/coleta-inicial`, 20 arquivos), que cobrem de 1º/10 até o início das coletas diárias, foram feitas numa sessão anterior. Os arquivos não registram a query usada. A partir das coletas diárias, as buscas seguem exatamente as tabelas acima, que estão no `AGENTE.md`.
