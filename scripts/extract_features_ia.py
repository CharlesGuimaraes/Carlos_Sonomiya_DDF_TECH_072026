"""
Extração de Features via IA - HM E-commerce Products
Case Técnico Dadosfera - Item 5 (Processar)

Usa a API da Groq (LLM) para ler a descrição livre do produto (detail_desc)
e extrair atributos estruturados em JSON: material, estilo, público-alvo,
ocasião de uso e estação sugerida.

Roda numa AMOSTRA do dataset (não no total de 105k) por eficiência de tempo/custo.
A lógica é a mesma e escala para o dataset completo apenas ajustando SAMPLE_SIZE.

Requisitos:
    pip install groq pandas

Uso:
    export GROQ_API_KEY="sua_chave_aqui"      (Linux/Mac)
    set GROQ_API_KEY=sua_chave_aqui           (Windows cmd)
    $env:GROQ_API_KEY="sua_chave_aqui"        (Windows PowerShell)

    python extract_features_ia.py
"""

import os
import json
import time
import pandas as pd
from groq import Groq

CSV_PATH = "hm_ecommerce_products.csv"
OUTPUT_CSV = "produtos_features_ia.csv"
OUTPUT_JSON = "produtos_features_ia.json"

SAMPLE_SIZE = 300          # quantidade de produtos a processar
MODEL = "llama-3.1-8b-instant"   # rápido e barato, bom para extração estruturada
SLEEP_BETWEEN_CALLS = 0.3  # evita estourar rate limit do free tier

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """Você é um extrator de atributos de produtos de moda.
Dada a descrição de um produto, extraia SOMENTE um JSON válido com os campos:

{
  "material_predominante": "string curta ou 'não especificado'",
  "estilo": "string curta (ex: casual, esportivo, elegante, básico)",
  "publico_alvo": "string curta (ex: feminino adulto, infantil, unissex)",
  "ocasiao_de_uso": "string curta (ex: dia a dia, festa, trabalho, praia)",
  "estacao_sugerida": "string curta (ex: verão, inverno, todas as estações)"
}

Responda APENAS com o JSON, sem texto adicional, sem markdown, sem explicações.
Se a descrição não tiver informação suficiente para algum campo, use "não especificado".
"""


def extrair_features(descricao: str) -> dict:
    if not descricao or str(descricao).strip() == "" or str(descricao).lower() == "nan":
        return {
            "material_predominante": "não especificado",
            "estilo": "não especificado",
            "publico_alvo": "não especificado",
            "ocasiao_de_uso": "não especificado",
            "estacao_sugerida": "não especificado",
        }

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Descrição do produto: {descricao}"},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"  [erro] {e}")
        return {
            "material_predominante": "erro_processamento",
            "estilo": "erro_processamento",
            "publico_alvo": "erro_processamento",
            "ocasiao_de_uso": "erro_processamento",
            "estacao_sugerida": "erro_processamento",
        }


def main():
    if not os.environ.get("GROQ_API_KEY"):
        print("ERRO: variável de ambiente GROQ_API_KEY não encontrada.")
        print("Configure antes de rodar: set GROQ_API_KEY=sua_chave (Windows cmd)")
        return

    print(f"Carregando {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH)
    print(f"Dataset completo: {len(df)} linhas")

    # amostra aleatória reprodutível
    df_sample = df.sample(n=min(SAMPLE_SIZE, len(df)), random_state=42).reset_index(drop=True)
    print(f"Processando amostra de {len(df_sample)} produtos via Groq ({MODEL})...\n")

    resultados = []
    for i, row in df_sample.iterrows():
        descricao = row.get("detail_desc", "")
        print(f"[{i+1}/{len(df_sample)}] article_id={row.get('article_id')} - processando...")

        features = extrair_features(descricao)

        resultado = {
            "article_id": row.get("article_id"),
            "prod_name": row.get("prod_name"),
            "detail_desc": descricao,
            **features,
        }
        resultados.append(resultado)
        time.sleep(SLEEP_BETWEEN_CALLS)

    df_resultado = pd.DataFrame(resultados)
    df_resultado.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    df_resultado.to_json(OUTPUT_JSON, orient="records", force_ascii=False, indent=2)

    print(f"\nConcluído! {len(df_resultado)} produtos processados.")
    print(f"Salvo em: {OUTPUT_CSV} e {OUTPUT_JSON}")
    print("\nAmostra do resultado:")
    print(df_resultado[["prod_name", "material_predominante", "estilo", "publico_alvo"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()