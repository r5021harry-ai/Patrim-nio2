import streamlit as st
import pandas as pd

def render_dashboard(patrimonio_db):
    st.title("Dashboard Geral")

    if not patrimonio_db:
        st.info("Nenhum dado patrimonial cadastrado para exibição.")
        return

    df = pd.DataFrame(patrimonio_db)

    # Mapeamento de colunas (com fallbacks flexíveis para maiúsculas/minúsculas)
    col_etiqueta = next((c for c in ['etiqueta', 'patrimonio', 'Etiqueta', 'Patrimônio'] if c in df.columns), df.columns[0])
    col_categoria = next((c for c in ['categoria', 'tipo', 'Categoria', 'Tipo'] if c in df.columns), None)
    col_status = next((c for c in ['status', 'estado', 'Status', 'Estado'] if c in df.columns), None)
    col_local = next((c for c in ['localizacao', 'cidade', 'Localização', 'Cidade'] if c in df.columns), None)

    # Cartões de Métricas (KPIs)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de Bens", len(df))

    if col_status:
        # Busca insensível a maiúsculas/minúsculas para capturar variações do status
        status_series = df[col_status].astype(str).str.strip().str.lower()
        
        qtd_disp = len(df[status_series.isin(["disponível", "disponivel", "bom", "novo"])])
        qtd_uso = len(df[status_series.isin(["em uso", "uso", "alocado"])])
        qtd_manut = len(df[status_series.isin(["manutenção", "manutencao", "reparo"])])
    else:
        qtd_disp, qtd_uso, qtd_manut = 0, 0, 0

    c2.metric("Disponíveis", qtd_disp)
    c3.metric("Em Uso", qtd_uso)
    c4.metric("Em Manutenção", qtd_manut)

    st.divider()

    # Gráficos e Distribuição de Dados
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("**Bens por Categoria**")
        if col_categoria:
            cat_counts = df[col_categoria].astype(str).value_counts().reset_index()
            cat_counts.columns = ["Categoria", "Quantidade"]
            st.bar_chart(cat_counts.set_index("Categoria"), color="#15803D")
        else:
            st.caption("Coluna de categoria não encontrada.")

    with col_g2:
        st.markdown("**Bens por Localização**")
        if col_local:
            loc_counts = df[col_local].astype(str).value_counts().reset_index()
            loc_counts.columns = ["Localização", "Quantidade"]
            st.bar_chart(loc_counts.set_index("Localização"), color="#15803D")
        else:
            st.caption("Coluna de localização não encontrada.")

    st.divider()

    # Tabela Resumida por Categoria e Status
    st.markdown("**Resumo por Categoria e Status**")
    if col_categoria and col_status:
        df_cat_status = df.groupby([col_categoria, col_status]).size().unstack(fill_value=0)
        st.dataframe(df_cat_status, use_container_width=True)
    else:
        st.caption("Dados insuficientes para cruzar Categoria e Status.")
