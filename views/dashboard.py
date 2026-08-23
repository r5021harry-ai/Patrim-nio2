import streamlit as st
import pandas as pd

def render_dashboard(patrimonio_db):
    st.title("📊 Dashboard Geral")

    if not patrimonio_db:
        st.info("Nenhum dado patrimonial cadastrado para exibição.")
        return

    df = pd.DataFrame(patrimonio_db)

    # Identificação dinâmica de colunas
    col_etiqueta = 'etiqueta' if 'etiqueta' in df.columns else 'patrimonio'
    col_categoria = 'categoria' if 'categoria' in df.columns else 'tipo'
    col_status = 'status' if 'status' in df.columns else 'estado'
    col_local = 'localizacao' if 'localizacao' in df.columns else 'cidade'

    # Cartões de Métricas (KPIS)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de Bens", len(df))
    
    qtd_disp = len(df[df[col_status] == "Disponível"]) if col_status in df.columns else 0
    c2.metric("Disponíveis", qtd_disp)

    qtd_uso = len(df[df[col_status] == "Em Uso"]) if col_status in df.columns else 0
    c3.metric("Em Uso", qtd_uso)

    qtd_manut = len(df[df[col_status] == "Manutenção"]) if col_status in df.columns else 0
    c4.metric("Em Manutenção", qtd_manut)

    st.divider()

    # Gráficos e Distribuição de Dados
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("📌 Bens por Categoria")
        if col_categoria in df.columns:
            # Agregação segura sem erro de coluna duplicada
            cat_counts = df[col_categoria].value_counts().reset_index()
            cat_counts.columns = ["Categoria", "Quantidade"]
            st.bar_chart(cat_counts.set_index("Categoria"))
        else:
            st.caption("Coluna de categoria não encontrada.")

    with col_g2:
        st.subheader("📍 Bens por Localização")
        if col_local in df.columns:
            loc_counts = df[col_local].value_counts().reset_index()
            loc_counts.columns = ["Localização", "Quantidade"]
            st.bar_chart(loc_counts.set_index("Localização"))
        else:
            st.caption("Coluna de localização não encontrada.")

    st.divider()

    # Tabela Resumida por Categoria e Status (Corrigida)
    st.subheader("📋 Resumo por Categoria e Status")
    if col_categoria in df.columns and col_status in df.columns:
        # Agrupamento seguro com count() explícito
        df_cat_status = df.groupby([col_categoria, col_status]).size().unstack(fill_value=0)
        st.dataframe(df_cat_status, use_container_width=True)
