import pandas as pd

df = pd.read_parquet("hm_ecommerce_products.parquet")

colunas_para_remover = ["dense_embedding", "sparse_indices", "sparse_values"]
df = df.drop(columns=colunas_para_remover)

df.to_csv("hm_ecommerce_products.csv", index=False)
print(f"Convertido! {len(df)} linhas, {len(df.columns)} colunas.")