"""
Geração de Vendas Simuladas - HM E-commerce Products
Case Técnico Dadosfera - Suporte ao Item 7 (Dashboard / Série Temporal)

O dataset de origem (catálogo H&M) não contém transações com data,
apenas metadados de produto. Para viabilizar a análise de série temporal
exigida no dashboard, este script gera um conjunto de vendas SIMULADAS
ao longo dos últimos 12 meses, associadas aos produtos reais do catálogo.

Isso é uma decisão de escopo documentada — os dados de produto são reais,
as transações de venda são sintéticas para fins de demonstração analítica.

Uso:
    python gerar_vendas_simuladas.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

CATALOGO_PATH = "hm_ecommerce_products.csv"
FEATURES_IA_PATH = "produtos_features_ia.csv"
OUTPUT_PATH = "vendas_simuladas.csv"

MESES_HISTORICO = 12
SEED = 42

np.random.seed(SEED)

print("Carregando dados...")
catalogo = pd.read_csv(CATALOGO_PATH)
features_ia = pd.read_csv(FEATURES_IA_PATH)

# Usamos apenas os produtos que já têm features de IA (amostra de 300),
# assim as vendas simuladas já vêm prontas para cruzar com estilo/público-alvo/estação.
produtos = features_ia.merge(
    catalogo[["article_id", "prod_name", "department_name", "product_group_name", "colour_group_name"]],
    on="article_id",
    how="left",
    suffixes=("", "_cat"),
)

print(f"Gerando vendas simuladas para {len(produtos)} produtos ao longo de {MESES_HISTORICO} meses...")

data_fim = datetime(2026, 7, 1)
data_inicio = data_fim - timedelta(days=30 * MESES_HISTORICO)

# preço base simulado por produto (varia por estilo, só para dar realismo)
faixa_preco = {
    "casual": (49.9, 129.9),
    "elegante": (99.9, 249.9),
    "esportivo": (69.9, 159.9),
    "básico": (29.9, 79.9),
}

registros = []
sale_id = 1

for _, row in produtos.iterrows():
    estilo = str(row.get("estilo", "casual")).lower()
    preco_min, preco_max = faixa_preco.get(estilo, (49.9, 129.9))
    preco_unitario = round(np.random.uniform(preco_min, preco_max), 2)

    # cada produto gera entre 5 e 40 vendas ao longo do período
    n_vendas = np.random.randint(5, 41)

    # sazonalidade simples: produtos de "verão" vendem mais em dez-mar,
    # "inverno" vendem mais em jun-ago (hemisfério sul)
    estacao = str(row.get("estacao_sugerida", "")).lower()

    for _ in range(n_vendas):
        dias_offset = np.random.randint(0, 30 * MESES_HISTORICO)
        data_venda = data_inicio + timedelta(days=dias_offset)
        mes = data_venda.month

        peso = 1.0
        if "verão" in estacao and mes in [12, 1, 2, 3]:
            peso = 1.8
        elif "inverno" in estacao and mes in [6, 7, 8]:
            peso = 1.8

        if np.random.random() > (peso / 2):
            continue

        quantidade = np.random.randint(1, 4)
        registros.append({
            "sale_id": sale_id,
            "article_id": row["article_id"],
            "prod_name": row["prod_name"],
            "department_name": row.get("department_name"),
            "product_group_name": row.get("product_group_name"),
            "estilo": row.get("estilo"),
            "publico_alvo": row.get("publico_alvo"),
            "estacao_sugerida": row.get("estacao_sugerida"),
            "data_venda": data_venda.strftime("%Y-%m-%d"),
            "quantidade": quantidade,
            "preco_unitario": preco_unitario,
            "receita": round(quantidade * preco_unitario, 2),
        })
        sale_id += 1

df_vendas = pd.DataFrame(registros)
df_vendas.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

print(f"\nGerado: {OUTPUT_PATH}")
print(f"Total de transações simuladas: {len(df_vendas)}")
print(f"Período: {df_vendas['data_venda'].min()} a {df_vendas['data_venda'].max()}")
print(f"Receita total simulada: R$ {df_vendas['receita'].sum():,.2f}")