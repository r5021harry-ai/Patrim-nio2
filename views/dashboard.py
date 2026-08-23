import streamlit as st
import pandas as pd
import plotly.express as px

def render_dashboard(patrimonio_db):
    st.title("📊 Dashboard - Patrimônio ISPN")
    df = pd.DataFrame(patrimonio_db)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Bens", len(df))
    col2.metric("Disponíveis", len(df[df["status"] == "Disponível"]) if not df.empty else 0)
    col3.metric("Em Uso", len(df[df["status"] == "Em Uso"]) if not df.empty else 0)
    col4.metric("Em Manutenção", len(df[df["status"] == "Em Manutenção"]) if not df.empty else 0)

    st.markdown("---")

    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📍 Alocação por Localização")
            fig_loc = px.pie(df, names="localizacao", title="Distribuição por Local", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_loc, width="stretch")

        with c2:
            st.subheader("📂 Distribuição por Categoria ISPN")
            fig_cat = px.bar(df, x="categoria", color="status", title="Patrimônios por Categoria e Status", barmode="stack")
            st.plotly_chart(fig_cat, width="stretch")
    else:
        st.info("Nenhum patrimônio cadastrado no momento.")
