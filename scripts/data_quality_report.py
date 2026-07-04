"""
Relatório de Qualidade de Dados - HM E-commerce Products
Case Técnico Dadosfera

Gera um relatório em Markdown e HTML cobrindo as dimensões clássicas
de qualidade de dados (as mesmas avaliadas por ferramentas como
Great Expectations e Soda Core):

  - Completude (valores nulos/vazios)
  - Unicidade (duplicatas, chaves)
  - Validade (formatos, domínios esperados)
  - Consistência (relações entre colunas)

Uso:
    python data_quality_report.py
(coloque este script na mesma pasta do arquivo hm_ecommerce_products.csv)
"""

import pandas as pd
from datetime import datetime

CSV_PATH = "hm_ecommerce_products.csv"
OUTPUT_MD = "data_quality_report.md"
OUTPUT_HTML = "data_quality_report.html"

# Colunas que esperamos ser únicas (chave primária)
UNIQUE_KEY_COLS = ["article_id"]

# Pares (código, nome) que devem ter mapeamento 1-para-1 consistente
CONSISTENCY_PAIRS = [
    ("department_no", "department_name"),
    ("colour_group_code", "colour_group_name"),
    ("product_type_no", "product_type_name"),
    ("garment_group_no", "garment_group_name"),
    ("index_group_no", "index_group_name"),
    ("section_no", "section_name"),
    ("graphical_appearance_no", "graphical_appearance_name"),
]


def load_data(path):
    print(f"Carregando {path} ...")
    df = pd.read_csv(path)
    print(f"Carregado: {len(df)} linhas, {len(df.columns)} colunas")
    return df


def completude(df):
    rows = []
    for col in df.columns:
        total = len(df)
        nulos = df[col].isna().sum()
        vazios = 0
        if df[col].dtype == object:
            vazios = (df[col].astype(str).str.strip() == "").sum()
        pct_completo = 100 * (1 - (nulos + vazios) / total) if total else 0
        rows.append({
            "coluna": col,
            "nulos": int(nulos),
            "vazios": int(vazios),
            "pct_completude": round(pct_completo, 2),
        })
    return pd.DataFrame(rows).sort_values("pct_completude")


def unicidade(df):
    rows = []
    for col in UNIQUE_KEY_COLS:
        if col not in df.columns:
            continue
        total = len(df)
        distintos = df[col].nunique()
        duplicados = total - distintos
        rows.append({
            "coluna": col,
            "total_linhas": total,
            "valores_distintos": distintos,
            "duplicados": duplicados,
            "status": "OK - chave única" if duplicados == 0 else "ALERTA - possui duplicatas",
        })

    linhas_duplicadas = df.duplicated().sum()
    rows.append({
        "coluna": "(linha inteira)",
        "total_linhas": len(df),
        "valores_distintos": len(df) - linhas_duplicadas,
        "duplicados": int(linhas_duplicadas),
        "status": "OK" if linhas_duplicadas == 0 else "ALERTA - linhas totalmente duplicadas",
    })
    return pd.DataFrame(rows)


def validade(df):
    checks = []

    # 1. IDs devem ser positivos e não nulos
    if "article_id" in df.columns:
        invalidos = df["article_id"].isna().sum()
        checks.append({
            "regra": "article_id não nulo",
            "violacoes": int(invalidos),
            "status": "OK" if invalidos == 0 else "FALHOU",
        })

    # 2. Colunas de texto não devem ter tamanho absurdo (ex: erro de parsing)
    if "detail_desc" in df.columns:
        vazio_desc = df["detail_desc"].isna().sum()
        muito_curto = df["detail_desc"].astype(str).str.len().lt(5).sum()
        checks.append({
            "regra": "detail_desc preenchida (não nula)",
            "violacoes": int(vazio_desc),
            "status": "OK" if vazio_desc == 0 else "ALERTA",
        })
        checks.append({
            "regra": "detail_desc com conteúdo mínimo (>=5 caracteres)",
            "violacoes": int(muito_curto),
            "status": "OK" if muito_curto == 0 else "ALERTA",
        })

    # 3. Colunas numéricas de código devem ser >= 0
    numeric_code_cols = [c for c in df.columns if c.endswith("_no") or c.endswith("_id") or c.endswith("_code")]
    for col in numeric_code_cols:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            negativos = (df[col] < 0).sum()
            checks.append({
                "regra": f"{col} >= 0",
                "violacoes": int(negativos),
                "status": "OK" if negativos == 0 else "FALHOU",
            })

    # 4. image_url deve começar com http
    if "image_url" in df.columns:
        invalid_url = (~df["image_url"].astype(str).str.startswith("http")).sum()
        checks.append({
            "regra": "image_url formato válido (http...)",
            "violacoes": int(invalid_url),
            "status": "OK" if invalid_url == 0 else "ALERTA",
        })

    return pd.DataFrame(checks)


def consistencia(df):
    rows = []
    for code_col, name_col in CONSISTENCY_PAIRS:
        if code_col not in df.columns or name_col not in df.columns:
            continue
        mapping = df.groupby(code_col)[name_col].nunique()
        inconsistentes = (mapping > 1).sum()
        rows.append({
            "par": f"{code_col} -> {name_col}",
            "codigos_com_mais_de_1_nome": int(inconsistentes),
            "status": "OK - mapeamento consistente" if inconsistentes == 0 else "ALERTA - mapeamento inconsistente",
        })
    return pd.DataFrame(rows)


def gerar_relatorio(df):
    comp = completude(df)
    uniq = unicidade(df)
    val = validade(df)
    cons = consistencia(df)

    total_linhas = len(df)
    total_colunas = len(df.columns)
    score_completude = comp["pct_completude"].mean()

    md = []
    md.append("# Relatório de Qualidade de Dados")
    md.append(f"\n**Dataset:** hm_ecommerce_products.csv  ")
    md.append(f"**Data da análise:** {datetime.now().strftime('%d/%m/%Y %H:%M')}  ")
    md.append(f"**Total de linhas:** {total_linhas:,}  ")
    md.append(f"**Total de colunas:** {total_colunas}  ")
    md.append(f"**Score médio de completude:** {score_completude:.2f}%\n")

    md.append("## 1. Completude (valores nulos/vazios por coluna)\n")
    md.append(comp.to_markdown(index=False))

    md.append("\n\n## 2. Unicidade (duplicatas e chaves)\n")
    md.append(uniq.to_markdown(index=False))

    md.append("\n\n## 3. Validade (regras de domínio e formato)\n")
    md.append(val.to_markdown(index=False))

    md.append("\n\n## 4. Consistência (mapeamento código -> nome)\n")
    md.append(cons.to_markdown(index=False))

    md.append("\n\n## 5. Conclusão\n")
    falhas = (val["status"] == "FALHOU").sum() if not val.empty else 0
    alertas = (
        (val["status"] == "ALERTA").sum() if not val.empty else 0
    ) + (
        (cons["status"].str.contains("ALERTA")).sum() if not cons.empty else 0
    )
    if falhas == 0 and alertas == 0:
        md.append("Dataset aprovado em todas as verificações de qualidade aplicadas. "
                   "Nenhuma falha crítica ou alerta identificado.")
    else:
        md.append(f"Foram identificadas **{falhas} falha(s) crítica(s)** e **{alertas} alerta(s)**. "
                   "Ver detalhes nas seções acima. Nenhuma falha impede o uso do dataset "
                   "para os fins deste case, mas ficam documentadas como pontos de atenção.")

    md_text = "\n".join(md)

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md_text)

    html = f"<html><head><meta charset='utf-8'><title>Data Quality Report</title></head><body>"
    html += "<pre style='font-family:monospace; white-space:pre-wrap;'>" + md_text + "</pre></body></html>"
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nRelatório gerado com sucesso:")
    print(f"  - {OUTPUT_MD}")
    print(f"  - {OUTPUT_HTML}")
    print(f"\nResumo: {total_linhas:,} linhas | completude média {score_completude:.2f}% | "
          f"{falhas} falha(s) | {alertas} alerta(s)")


if __name__ == "__main__":
    df = load_data(CSV_PATH)
    gerar_relatorio(df)