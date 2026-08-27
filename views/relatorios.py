import streamlit as st
import pandas as pd

def render_relatorios(patrimonio_db, historico_db):
    # Título removido para evitar duplicidade com a navegação
    st.caption("Consulte a relação geral dos bens e o histórico de movimentações do sistema.")

    tab_geral, tab_historico = st.tabs(["Relação Geral & Filtros", "Histórico Geral do Sistema"])

    with tab_geral:
        st.subheader("Relação Geral de Patrimônios")

        if not patrimonio_db:
            st.info("Nenhum patrimônio cadastrado.")
        else:
            df = pd.DataFrame(patrimonio_db)

            col_f1, col_f2 = st.columns(2)
            
            col_status = next((c for c in ['status', 'estado', 'Status', 'Estado'] if c in df.columns), None)
            col_local = next((c for c in ['localizacao', 'cidade', 'Localização', 'Cidade'] if c in df.columns), None)

            with col_f1:
                if col_status:
                    opcoes_status = ["Todos"] + sorted(df[col_status].dropna().astype(str).unique().tolist())
                    filtro_status = st.selectbox("Filtrar por Status:", opcoes_status)
                else:
                    filtro_status = "Todos"

            with col_f2:
                if col_local:
                    opcoes_local = ["Todos"] + sorted(df[col_local].dropna().astype(str).unique().tolist())
                    filtro_local = st.selectbox("Filtrar por Localização:", opcoes_local)
                else:
                    filtro_local = "Todos"

            df_filtrado = df.copy()
            if filtro_status != "Todos" and col_status:
                df_filtrado = df_filtrado[df_filtrado[col_status].astype(str) == filtro_status]
            if filtro_local != "Todos" and col_local:
                df_filtrado = df_filtrado[df_filtrado[col_local].astype(str) == filtro_local]

            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Baixar Relatório (CSV)",
                data=csv,
                file_name="relatorio_patrimonio.csv",
                mime="text/csv"
            )

    with tab_historico:
        st.subheader("Histórico de Movimentações")

        if not historico_db:
            st.info("Nenhuma movimentação registrada até o momento.")
        else:
            df_hist = pd.DataFrame(historico_db)
            
            if "data_hora" in df_hist.columns:
                df_hist = df_hist.sort_values(by="data_hora", ascending=False)

            st.dataframe(df_hist, use_container_width=True, hide_index=True)

            csv_hist = df_hist.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Baixar Histórico (CSV)",
                data=csv_hist,
                file_name="historico_patrimonio.csv",
                mime="text/csv"
            )
