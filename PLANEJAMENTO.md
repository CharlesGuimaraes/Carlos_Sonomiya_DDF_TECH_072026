# Planejamento do Projeto — Case Técnico Dadosfera

Metodologia: quadro Kanban simplificado, com marcos diários dentro do prazo
de 5 dias corridos.

## Backlog → Em Andamento → Concluído

### Dia 1 — Fundação
- [x] Escolha do dataset (H&M E-commerce, Hugging Face)
- [x] Criação do repositório GitHub
- [x] Cadastro e acesso à plataforma Dadosfera
- [x] Conversão parquet → CSV (remoção de embeddings)
- [x] Integração: upload do dataset na Dadosfera

### Dia 2 — Qualidade e Catalogação
- [x] Catalogação do dataset (Explorar → Catálogo)
- [x] Documentação do dicionário de dados
- [x] Relatório de qualidade de dados (completude, unicidade, validade, consistência)

### Dia 3 — IA e Modelagem
- [x] Extração de features via IA (Groq API) — amostra de 300 produtos
- [x] Modelagem dimensional (Kimball) — dimensões, fato e 2 visões finais
- [x] Adaptação: modelagem executada localmente devido a bloqueio do módulo Transformação

### Dia 4 — Análise e Automação
- [x] Geração de vendas simuladas para viabilizar série temporal
- [x] Dashboard no Metabase (5 visualizações + série temporal)
- [x] Pipeline automatizada (Google Sheets → Dadosfera, agendamento 24h)
- [x] Data App em Streamlit (filtros, métricas, gráficos, busca)

### Dia 5 — Entrega
- [x] Organização do repositório (scripts, docs, app)
- [x] README completo com documentação de todos os itens
- [ ] Gravação do vídeo de apresentação
- [ ] Revisão final e submissão

## Riscos identificados e mitigação

| Risco | Mitigação |
|---|---|
| Dataset sem série temporal nativa | Geração de vendas simuladas documentada |
| Módulo de Transformação bloqueado | Modelagem replicada localmente em Python |
| Tamanho de arquivo acima do limite de upload | Remoção de colunas não essenciais |
| Prazo apertado (5 dias) | Priorização por nível de entrega (Avançado como meta) |