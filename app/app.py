"""
Data App - Case Técnico Dadosfera - Item 9
H&M E-commerce Analytics Explorer

App interativo em Streamlit para explorar o catálogo de produtos H&M,
enriquecido com atributos extraídos via IA, e as vendas simuladas geradas
para análise de série temporal.

Requisitos:
    pip install streamlit pandas plotly

Uso:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="H&M E-commerce Analytics",
    page_icon="🛍️",
    layout="wide",
)

# ------------------------------------------------------------
# CARREGAMENTO DE DADOS
# ------------------------------------------------------------

@st.cache_data
def carregar_dados():
    catalogo = pd.read_csv("vw_catalogo_enriquecido.csv")
    vendas = pd.read_csv("vendas_simuladas.csv")
    vendas["data_venda"] = pd.to_datetime(vendas["data_venda"])
    return catalogo, vendas


try:
    catalogo, vendas = carregar_dados()
except FileNotFoundError as e:
    st.error(
        f"Arquivo não encontrado: {e}. "
        "Certifique-se de que 'vw_catalogo_enriquecido.csv' e 'vendas_simuladas.csv' "
        "estão na mesma pasta deste app.py."
    )
    st.stop()

# ------------------------------------------------------------
# SIDEBAR - FILTROS
# ------------------------------------------------------------

st.sidebar.title("🛍️ Filtros")
st.sidebar.markdown("Ajuste os filtros para explorar o catálogo H&M.")

departamentos = st.sidebar.multiselect(
    "Departamento",
    options=sorted(catalogo["department_name"].dropna().unique()),
    default=[],
)

estilos = st.sidebar.multiselect(
    "Estilo (IA)",
    options=sorted(catalogo["estilo"].dropna().unique()),
    default=[],
)

publicos = st.sidebar.multiselect(
    "Público-alvo (IA)",
    options=sorted(catalogo["publico_alvo"].dropna().unique()),
    default=[],
)

estacoes = st.sidebar.multiselect(
    "Estação sugerida (IA)",
    options=sorted(catalogo["estacao_sugerida"].dropna().unique()),
    default=[],
)

# aplica filtros
df_filtrado = catalogo.copy()
if departamentos:
    df_filtrado = df_filtrado[df_filtrado["department_name"].isin(departamentos)]
if estilos:
    df_filtrado = df_filtrado[df_filtrado["estilo"].isin(estilos)]
if publicos:
    df_filtrado = df_filtrado[df_filtrado["publico_alvo"].isin(publicos)]
if estacoes:
    df_filtrado = df_filtrado[df_filtrado["estacao_sugerida"].isin(estacoes)]

vendas_filtrado = vendas.copy()
if departamentos:
    vendas_filtrado = vendas_filtrado[vendas_filtrado["department_name"].isin(departamentos)]
if estilos:
    vendas_filtrado = vendas_filtrado[vendas_filtrado["estilo"].isin(estilos)]
if publicos:
    vendas_filtrado = vendas_filtrado[vendas_filtrado["publico_alvo"].isin(publicos)]
if estacoes:
    vendas_filtrado = vendas_filtrado[vendas_filtrado["estacao_sugerida"].isin(estacoes)]

# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.title("🛍️ H&M E-commerce Analytics Explorer")
st.caption(
    "Case Técnico Dadosfera — catálogo real de produtos H&M enriquecido com "
    "atributos extraídos via IA (Groq/LLM) e vendas simuladas para análise de série temporal."
)

# ------------------------------------------------------------
# MÉTRICAS PRINCIPAIS
# ------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)
col1.metric("Produtos no catálogo", f"{len(df_filtrado):,}")
col2.metric("Produtos com features IA", f"{df_filtrado['estilo'].notna().sum():,}")
col3.metric("Receita simulada total", f"R$ {vendas_filtrado['receita'].sum():,.2f}")
col4.metric("Unidades vendidas (simulado)", f"{int(vendas_filtrado['quantidade'].sum()):,}")

st.divider()

# ------------------------------------------------------------
# ABAS
# ------------------------------------------------------------

tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "📈 Série Temporal", "🔎 Explorar Produtos"])

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Produtos por Categoria")
        contagem_categoria = (
            df_filtrado["product_group_name"].value_counts().reset_index()
        )
        contagem_categoria.columns = ["Categoria", "Total"]
        fig = px.bar(contagem_categoria, x="Total", y="Categoria", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Distribuição por Estilo (IA)")
        contagem_estilo = df_filtrado["estilo"].dropna().value_counts().reset_index()
        contagem_estilo.columns = ["Estilo", "Total"]
        fig = px.pie(contagem_estilo, names="Estilo", values="Total", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Distribuição por Público-Alvo (IA)")
        contagem_publico = df_filtrado["publico_alvo"].dropna().value_counts().reset_index()
        contagem_publico.columns = ["Público-alvo", "Total"]
        fig = px.bar(contagem_publico, x="Público-alvo", y="Total")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.subheader("Top 10 Cores mais comuns")
        contagem_cor = df_filtrado["colour_group_name"].value_counts().head(10).reset_index()
        contagem_cor.columns = ["Cor", "Total"]
        fig = px.bar(contagem_cor, x="Cor", y="Total")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Receita Simulada ao Longo do Tempo")

    if vendas_filtrado.empty:
        st.info("Nenhuma venda encontrada para os filtros selecionados.")
    else:
        vendas_mes = (
            vendas_filtrado
            .set_index("data_venda")
            .resample("MS")["receita"]
            .sum()
            .reset_index()
        )
        fig = px.line(vendas_mes, x="data_venda", y="receita", markers=True)
        fig.update_layout(xaxis_title="Mês", yaxis_title="Receita (R$)")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Sazonalidade por Estação Sugerida")
        vendas_estacao = (
            vendas_filtrado.groupby("estacao_sugerida")["quantidade"].sum().reset_index()
        )
        fig2 = px.bar(vendas_estacao, x="estacao_sugerida", y="quantidade")
        st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("Explorar Produtos")
    busca = st.text_input("Buscar por nome do produto")

    df_busca = df_filtrado
    if busca:
        df_busca = df_busca[df_busca["prod_name"].str.contains(busca, case=False, na=False)]

    st.write(f"{len(df_busca):,} produtos encontrados")
    st.dataframe(
        df_busca[[
            "article_id", "prod_name", "department_name", "product_group_name",
            "colour_group_name", "material_predominante", "estilo",
            "publico_alvo", "ocasiao_de_uso", "estacao_sugerida"
        ]],
        use_container_width=True,
        height=500,
    )

st.divider()
st.caption(
    "Nota: as vendas exibidas são simuladas para fins de demonstração analítica, "
    "já que o dataset de origem contém apenas metadados de catálogo, sem transações reais. "
    "Os dados de produto (nome, categoria, cor, descrição) são reais."
)