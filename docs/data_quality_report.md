# Relatório de Qualidade de Dados

**Dataset:** hm_ecommerce_products.csv  
**Data da análise:** 04/07/2026 16:02  
**Total de linhas:** 105,126  
**Total de colunas:** 27  
**Score médio de completude:** 100.00%

## 1. Completude (valores nulos/vazios por coluna)

| coluna                       |   nulos |   vazios |   pct_completude |
|:-----------------------------|--------:|---------:|-----------------:|
| article_id                   |       0 |        0 |              100 |
| product_code                 |       0 |        0 |              100 |
| prod_name                    |       0 |        0 |              100 |
| product_type_no              |       0 |        0 |              100 |
| product_type_name            |       0 |        0 |              100 |
| product_group_name           |       0 |        0 |              100 |
| graphical_appearance_no      |       0 |        0 |              100 |
| graphical_appearance_name    |       0 |        0 |              100 |
| colour_group_code            |       0 |        0 |              100 |
| colour_group_name            |       0 |        0 |              100 |
| perceived_colour_value_id    |       0 |        0 |              100 |
| perceived_colour_value_name  |       0 |        0 |              100 |
| perceived_colour_master_id   |       0 |        0 |              100 |
| perceived_colour_master_name |       0 |        0 |              100 |
| department_no                |       0 |        0 |              100 |
| department_name              |       0 |        0 |              100 |
| index_code                   |       0 |        0 |              100 |
| index_name                   |       0 |        0 |              100 |
| index_group_no               |       0 |        0 |              100 |
| index_group_name             |       0 |        0 |              100 |
| section_no                   |       0 |        0 |              100 |
| section_name                 |       0 |        0 |              100 |
| garment_group_no             |       0 |        0 |              100 |
| garment_group_name           |       0 |        0 |              100 |
| detail_desc                  |       0 |        0 |              100 |
| text_to_embed                |       0 |        0 |              100 |
| image_url                    |       0 |        0 |              100 |


## 2. Unicidade (duplicatas e chaves)

| coluna          |   total_linhas |   valores_distintos |   duplicados | status           |
|:----------------|---------------:|--------------------:|-------------:|:-----------------|
| article_id      |         105126 |              105126 |            0 | OK - chave única |
| (linha inteira) |         105126 |              105126 |            0 | OK               |


## 3. Validade (regras de domínio e formato)

| regra                                            |   violacoes | status   |
|:-------------------------------------------------|------------:|:---------|
| article_id não nulo                              |           0 | OK       |
| detail_desc preenchida (não nula)                |           0 | OK       |
| detail_desc com conteúdo mínimo (>=5 caracteres) |           0 | OK       |
| article_id >= 0                                  |           0 | OK       |
| product_code >= 0                                |           0 | OK       |
| product_type_no >= 0                             |         121 | FALHOU   |
| graphical_appearance_no >= 0                     |          52 | FALHOU   |
| colour_group_code >= 0                           |          28 | FALHOU   |
| perceived_colour_value_id >= 0                   |          28 | FALHOU   |
| perceived_colour_master_id >= 0                  |         684 | FALHOU   |
| department_no >= 0                               |           0 | OK       |
| index_group_no >= 0                              |           0 | OK       |
| section_no >= 0                                  |           0 | OK       |
| garment_group_no >= 0                            |           0 | OK       |
| image_url formato válido (http...)               |           0 | OK       |


## 4. Consistência (mapeamento código -> nome)

| par                                                  |   codigos_com_mais_de_1_nome | status                      |
|:-----------------------------------------------------|-----------------------------:|:----------------------------|
| department_no -> department_name                     |                            0 | OK - mapeamento consistente |
| colour_group_code -> colour_group_name               |                            0 | OK - mapeamento consistente |
| product_type_no -> product_type_name                 |                            0 | OK - mapeamento consistente |
| garment_group_no -> garment_group_name               |                            0 | OK - mapeamento consistente |
| index_group_no -> index_group_name                   |                            0 | OK - mapeamento consistente |
| section_no -> section_name                           |                            0 | OK - mapeamento consistente |
| graphical_appearance_no -> graphical_appearance_name |                            0 | OK - mapeamento consistente |


## 5. Conclusão

Foram identificadas **5 falha(s) crítica(s)** e **0 alerta(s)**. Ver detalhes nas seções acima. Nenhuma falha impede o uso do dataset para os fins deste case, mas ficam documentadas como pontos de atenção.