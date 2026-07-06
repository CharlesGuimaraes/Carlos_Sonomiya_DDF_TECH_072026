# Case Técnico Dadosfera — H&M E-commerce Analytics

Case técnico desenvolvido para o processo seletivo da Dadosfera, cobrindo o
ciclo de vida completo dos dados: ingestão, catalogação, qualidade, IA,
modelagem, análise, pipeline e Data App.

**Candidato:** Carlos Gabriel Guimarães Sonomiya
**Prazo:** 5 dias corridos

---

## 1. Escolha do dataset

**Dataset:** [H&M E-commerce Products](https://huggingface.co/datasets/Qdrant/hm_ecommerce_products) (Hugging Face)
**Volume:** 105.126 registros, 28 colunas originais (colunas de embeddings vetoriais
removidas por não serem necessárias ao escopo do case).

**Por que esse dataset:**
- Ultrapassa o mínimo de 100 mil registros exigido.
- Contém uma coluna de texto livre rica (`detail_desc`), ideal para a etapa de
  extração de features via IA (Item 5) — diferencial em relação a datasets
  puramente transacionais.
- Contexto de moda/e-commerce, aderente ao perfil de clientes atendidos pelo
  candidato como desenvolvedor freelancer.

---

## 2. Estrutura do repositório

```
├── data/
│   └── README.md              -> instruções para obter o dataset (não versionado)
├── docs/
│   ├── data_quality_report.md
│   ├── data_quality_report.html
│   └── prints/                -> evidências visuais de cada etapa
├── scripts/
│   ├── converter.py            -> parquet -> CSV (remoção de embeddings)
│   ├── data_quality_report.py  -> Item 4: relatório de qualidade de dados
│   ├── extract_features_ia.py  -> Item 5: extração de features via IA (Groq)
│   ├── modelagem_local.py      -> Item 6: modelagem dimensional (Kimball)
│   ├── gerar_vendas_simuladas.py -> apoio ao Item 7 (série temporal)
├── app/
│   └── app.py                  -> Item 9: Data App (Streamlit)
└── README.md
```

---

## 3. Itens desenvolvidos

### Item 0 — Planejamento
Planejamento executado de forma incremental ao longo dos 5 dias, priorizando:
(1) fundação e ingestão, (2) qualidade e IA, (3) modelagem e análise,
(4) pipeline e Data App, (5) apresentação final.

### Item 1 — Escolha da base de dados
Ver seção 1 acima.

### Item 2.1 — Integrar
Dataset importado na Dadosfera via módulo **Coletar → Importar arquivos**.
O arquivo original em Parquet (906MB, incluindo embeddings) foi convertido
localmente para CSV (`scripts/converter.py`), removendo as colunas
`dense_embedding`, `sparse_indices` e `sparse_values`, não utilizadas no
escopo deste case. Resultado: 105.126 linhas, 27 colunas.

### Item 3 — Explorar / Catalogar
Dataset catalogado no módulo **Explorar → Catálogo** da Dadosfera, com
descrição geral do dataset preenchida. A edição de descrição por coluna
individual não estava disponível na interface de candidato — dicionário de
dados completo documentado abaixo.

**Dicionário de dados (principais colunas):**

| Coluna | Descrição |
|---|---|
| article_id | Identificador único do produto |
| product_code | Código que agrupa variações do mesmo produto |
| prod_name | Nome comercial do produto |
| product_type_name | Tipo específico (ex: Vest top, Bra) |
| product_group_name | Categoria macro (ex: Garment Upper Body) |
| colour_group_name | Cor do produto |
| department_name | Departamento dentro da loja |
| index_name / index_group_name | Segmento (ex: Ladies, Divided) |
| section_name | Seção dentro do índice |
| garment_group_name | Grupo de categoria de vestuário |
| detail_desc | Descrição textual livre — base da extração via IA |
| image_url | URL da imagem do produto |

### Item 4 — Data Quality
Relatório de qualidade gerado via script Python (`scripts/data_quality_report.py`),
cobrindo as 4 dimensões clássicas de qualidade de dados:
- **Completude** — nulos/vazios por coluna
- **Unicidade** — verificação de chave primária (`article_id`) e linhas duplicadas
- **Validade** — regras de domínio (IDs não-negativos, descrições não vazias,
  URLs de imagem válidas)
- **Consistência** — verificação de mapeamento 1-para-1 entre códigos e nomes
  (ex: `department_no` ↔ `department_name`)

Relatório completo disponível em `docs/data_quality_report.md` e
`docs/data_quality_report.html`.

### Item 5 — Processar (IA)
Extração de atributos estruturados a partir da descrição textual (`detail_desc`)
usando a API da **Groq** (modelo `llama-3.1-8b-instant`), via
`scripts/extract_features_ia.py`.

Atributos extraídos:
- Material predominante
- Estilo (casual, elegante, esportivo...)
- Público-alvo
- Ocasião de uso
- Estação sugerida

**Decisão de escopo:** processada uma amostra de 300 produtos (não os 105 mil),
por eficiência de tempo/custo de API. A lógica é idêntica e escalável para o
dataset completo apenas ajustando o parâmetro `SAMPLE_SIZE`.

### Item 6 — Modelagem de dados
Modelo dimensional (Kimball / esquema estrela) com:
- **Dimensões:** `dim_produto`, `dim_categoria`, `dim_cor`, `dim_features_ia`
- **Fato:** `fato_produto`
- **2 visões analíticas finais:**
  - `vw_catalogo_enriquecido_v2` — catálogo completo com todas as dimensões
    e features de IA (105.126 linhas, uma por produto)
  - `vw_resumo_categoria_estilo` — agregado por categoria/estilo/público (216 linhas)

**Nota sobre a ferramenta:** o módulo **Transformação** da Dadosfera (SQL nativo
na plataforma) requer contratação e não estava disponível no acesso de
candidato. A modelagem foi executada localmente em Python
(`scripts/modelagem_local.py`), replicando a mesma lógica relacional que seria
aplicada via SQL, e os resultados finais foram importados de volta como
datasets na Dadosfera.

**Nota sobre versionamento no Catálogo:** a plataforma não oferece opção de
exclusão de ativos importados via interface de candidato. Uma primeira versão
de `vw_catalogo_enriquecido` continha duplicidade por explosão de merge
(dimensões sem deduplicação por chave) e foi corrigida na versão `_v2`, que é
a versão válida e utilizada nas etapas seguintes.

### Item 7 — Analisar (Dashboard)
Dashboard construído no **Metabase** (módulo Analisar → Visualização da
Dadosfera), com 5 visualizações e análise de série temporal:

1. **Receita Mensal** (linha) — série temporal, 12 meses
2. **Receita por Categoria de Produto** (barras)
3. **Distribuição de Produtos por Estilo** (pizza)
4. **Vendas por Estação Sugerida** (barras) — sazonalidade
5. **Top 10 Departamentos por Receita** (barras)

**Nota sobre série temporal:** o dataset de origem é um catálogo de produtos,
sem transações de venda reais. Para viabilizar a análise temporal exigida,
foi gerado um conjunto de **vendas simuladas** (`scripts/gerar_vendas_simuladas.py`),
associando os 300 produtos processados por IA a transações fictícias
distribuídas ao longo de 12 meses, com sazonalidade baseada na estação
sugerida via IA. Os dados de produto são reais; as transações de venda são
sintéticas, para fins de demonstração analítica.

### Item 8 — Pipelines
Pipeline criada no módulo **Coletar → Pipelines**, com fonte em Google Sheets
(planilha contendo o resumo agregado `vw_resumo_categoria_estilo`), destino na
tabela `resumo_categoria_estilo_pipeline` (schema PUBLIC), e agendamento de
sincronização a cada 24 horas. Simula um cenário de atualização periódica de
relatório gerencial a partir de uma planilha colaborativa.

### Item 9 — Data Apps
Aplicação interativa em **Streamlit** (`app/app.py`), rodando localmente,
com:
- Filtros por departamento, estilo, público-alvo e estação (todos derivados
  da extração via IA)
- Métricas principais (produtos, receita simulada, unidades vendidas)
- 3 abas: Visão Geral (4 gráficos), Série Temporal (receita mensal +
  sazonalidade), Explorar Produtos (busca + tabela filtrável)

**Como rodar:**
```bash
pip install streamlit pandas plotly
cd app
streamlit run app.py
```
(requer os arquivos `vw_catalogo_enriquecido.csv` e `vendas_simuladas.csv`
na mesma pasta — ver `data/README.md`)

### Item 10 — Apresentação final
Como a Dadosfera substituiria a arquitetura atual de um cliente de e-commerce:

1. **Centralização de dados dispersos** — catálogo, vendas e atendimento hoje
   costumam viver em sistemas separados (ERP, planilhas, plataforma de
   e-commerce). A Dadosfera centraliza ingestão e catalogação num só lugar,
   como demonstrado com o dataset H&M.
2. **Democratização de análise via IA** — a extração automática de atributos
   de produto (Item 5), hoje um trabalho manual de catalogação/merchandising,
   libera tempo do time de negócio e melhora a qualidade da informação
   disponível para busca, recomendação e segmentação.

---

## 4. Limitações identificadas e decisões de escopo

| Limitação | Decisão tomada |
|---|---|
| Módulo Transformação bloqueado (requer contratação) | Modelagem executada localmente em Python, resultados importados como datasets |
| Edição de descrição por coluna indisponível no Catálogo | Dicionário de dados documentado neste README |
| Dataset sem transações reais (necessário para série temporal) | Geração de vendas simuladas, claramente identificadas como sintéticas |
| Sem opção de exclusão de ativos no Catálogo | Versionamento por sufixo (`_v2`) documentado |
| Limite de 250MB por upload na Dadosfera | Remoção de colunas não essenciais (embeddings, URLs, descrições longas) das visões mais pesadas |

---

## 5. Tecnologias utilizadas

- **Dadosfera** — ingestão, catalogação, pipelines
- **Metabase** — dashboard analítico
- **Python** (pandas, groq) — conversão de dados, qualidade, IA, modelagem
- **Groq API** (llama-3.1-8b-instant) — extração de features via IA
- **Streamlit / Plotly** — Data App
- **Google Sheets** — fonte de dados do pipeline

---

## 6. Vídeo de apresentação

[Link do vídeo será adicionado aqui]