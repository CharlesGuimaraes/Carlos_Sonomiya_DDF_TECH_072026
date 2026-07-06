"""
Modelagem de Dados (Kimball / Esquema Estrela) - executado localmente
Case Técnico Dadosfera - Item 6

Alternativa ao módulo "Transformação" da Dadosfera, que está bloqueado
no acesso de candidato (requer contratação). A lógica de modelagem é
a mesma (dimensões + fato + views analíticas), só a ferramenta de
execução muda: SQL na plataforma -> pandas localmente.

Gera arquivos CSV prontos para subir na Dadosfera via "Importar arquivos".

Uso:
    python modelagem_local.py
"""

import pandas as pd

CATALOGO_PATH = "hm_ecommerce_products.csv"
FEATURES_IA_PATH = "produtos_features_ia.csv"

print("Carregando dados...")
catalogo = pd.read_csv(CATALOGO_PATH)
features_ia = pd.read_csv(FEATURES_IA_PATH)
print(f"Catálogo: {len(catalogo)} linhas | Features IA: {len(features_ia)} linhas")

# ------------------------------------------------------------
# DIMENSÕES
# ------------------------------------------------------------

dim_produto = catalogo[[
    "article_id", "product_code", "prod_name",
    "product_type_name", "product_group_name", "graphical_appearance_name"
]].drop_duplicates(subset=["article_id"])

dim_categoria = catalogo[[
    "department_no", "department_name", "index_name",
    "index_group_name", "section_name", "garment_group_name"
]].drop_duplicates(subset=["department_no"])

dim_cor = catalogo[[
    "colour_group_code", "colour_group_name",
    "perceived_colour_value_name", "perceived_colour_master_name"
]].drop_duplicates(subset=["colour_group_code"])

dim_features_ia = features_ia[[
    "article_id", "material_predominante", "estilo",
    "publico_alvo", "ocasiao_de_uso", "estacao_sugerida"
]].drop_duplicates(subset=["article_id"])

# ------------------------------------------------------------
# FATO
# ------------------------------------------------------------

fato_produto = catalogo[["article_id", "department_no", "colour_group_code", "detail_desc", "image_url"]]

# ------------------------------------------------------------
# VISÃO 1: Catálogo enriquecido (produto + categoria + cor + IA)
# ------------------------------------------------------------

vw_catalogo_enriquecido = (
    fato_produto
    .merge(dim_produto, on="article_id", how="left")
    .merge(dim_categoria, on="department_no", how="left")
    .merge(dim_cor, on="colour_group_code", how="left")
    .merge(dim_features_ia, on="article_id", how="left")
)

# Remove colunas de texto longo (detail_desc, image_url) para reduzir o
# tamanho do arquivo abaixo do limite de upload da Dadosfera (250MB).
# Essas colunas já estão documentadas no dataset original hm_ecommerce_products.
vw_catalogo_enriquecido = vw_catalogo_enriquecido.drop(columns=["detail_desc", "image_url"])

assert len(vw_catalogo_enriquecido) == len(fato_produto), (
    f"ALERTA: esperado {len(fato_produto)} linhas, mas vw_catalogo_enriquecido tem "
    f"{len(vw_catalogo_enriquecido)}. Há duplicidade em alguma dimensão."
)
print(f"Validação ok: vw_catalogo_enriquecido tem {len(vw_catalogo_enriquecido)} linhas (1 por produto).")

# ------------------------------------------------------------
# VISÃO 2: Resumo agregado por categoria e estilo
# ------------------------------------------------------------

vw_resumo_categoria_estilo = (
    vw_catalogo_enriquecido[vw_catalogo_enriquecido["estilo"].notna()]
    .groupby(
        ["department_name", "product_group_name", "estilo", "publico_alvo", "estacao_sugerida"],
        dropna=False,
    )
    .agg(total_produtos=("article_id", "count"))
    .reset_index()
    .sort_values("total_produtos", ascending=False)
)

# ------------------------------------------------------------
# SALVAR TUDO
# ------------------------------------------------------------

arquivos = {
    "dim_produto.csv": dim_produto,
    "dim_categoria.csv": dim_categoria,
    "dim_cor.csv": dim_cor,
    "dim_features_ia.csv": dim_features_ia,
    "fato_produto.csv": fato_produto,
    "vw_catalogo_enriquecido.csv": vw_catalogo_enriquecido,
    "vw_resumo_categoria_estilo.csv": vw_resumo_categoria_estilo,
}

for nome, df in arquivos.items():
    df.to_csv(nome, index=False, encoding="utf-8")
    print(f"Salvo: {nome} ({len(df)} linhas)")

print("\nModelagem concluída! Suba os arquivos vw_catalogo_enriquecido.csv e")
print("vw_resumo_categoria_estilo.csv na Dadosfera (Importar arquivos).")
print("As dimensões e o fato também podem ser subidos para documentar o modelo completo.")