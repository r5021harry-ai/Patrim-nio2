import streamlit as st
import pandas as pd
from datetime import datetime

def render_relatorios(patrimonio_db, historico_db, cidades_db=None):
    st.title("📑 Relatórios do Sistema")
    st.caption("Consulte a relação geral dos bens e o histórico de movimentações do sistema.")

    tab1, tab2 = st.tabs([
        "🔍 Relação Geral & Filtros", 
        "📜 Histórico Geral do Sistema"
    ])

    # --- TAB 1: RELAÇÃO GERAL & FILTROS ---
    with tab1:
        st.subheader("📊 Relação Geral de Patrimônios")
        
        if not patrimonio_db:
            st.warning("Nenhum patrimônio cadastrado.")
        else:
            df = pd.DataFrame(patrimonio_db)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                filtro_cidade = st.multiselect(
                    "Filtrar por Cidade / Unidade:",
                    options=sorted(df['cidade'].unique().tolist()) if 'cidade' in df.columns else []
                )
            with c2:
                filtro_estado = st.multiselect(
                    "Filtrar por Status / Estado:",
                    options=sorted(df['estado'].unique().tolist()) if 'estado' in df.columns else []
                )
            with c3:
                filtro_cat = st.multiselect(
                    "Filtrar por Categoria:",
                    options=sorted(df['categoria'].unique().tolist()) if 'categoria' in df.columns else []
                )

            df_filtrado = df.copy()
            if filtro_cidade and 'cidade' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['cidade'].isin(filtro_cidade)]
            if filtro_estado and 'estado' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['estado'].isin(filtro_estado)]
            if filtro_cat and 'categoria' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['categoria'].isin(filtro_cat)]

            st.dataframe(df_filtrado, use_container_width=True)
            
            # Exportar CSV
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exportar Tabela Filtrada (CSV)",
                data=csv,
                file_name=f"relatorio_patrimonio_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

    # --- TAB 2: HISTÓRICO GERAL DO SISTEMA ---
    with tab2:
        st.subheader("📜 Log de Atividades e Histórico Geral")
        if not historico_db:
            st.info("Nenhum histórico registrado no sistema até o momento.")
        else:
            df_hist = pd.DataFrame(historico_db)
            if "foto" in df_hist.columns:
                df_hist = df_hist.drop(columns=["foto"])
            st.dataframe(df_hist, use_container_width=True)
