import streamlit as st
import pandas as pd
from database.db import save_json, PATRIMONIO_FILE

def render_relatorios(patrimonio_db, historico_db):
    st.title("📑 Relatórios e Importação em Massa")
    df = pd.DataFrame(patrimonio_db)

    with st.expander("📥 Importar Planilha de Patrimônios Existentes (Excel / CSV)"):
        st.write("Upload de planilha contendo as colunas: `etiqueta`, `nome`, `categoria`, `localizacao`, `status`, `responsavel`")
        file_upload = st.file_uploader("Selecione sua planilha", type=["xlsx", "csv"])
        
        if file_upload is not None:
            try:
                if file_upload.name.endswith('.csv'):
                    df_imp = pd.read_csv(file_upload)
                else:
                    df_imp = pd.read_excel(file_upload)
                
                st.dataframe(df_imp.head())
                if st.button("Substituir / Carregar no Banco de Dados"):
                    novos_dados = df_imp.to_dict(orient="records")
                    st.session_state.patrimonio_db = novos_dados
                    save_json(PATRIMONIO_FILE, novos_dados)
                    st.success("Planilha importada e dados atualizados!")
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")

    st.markdown("---")
    st.subheader("🔍 Filtros e Exportação")
    if not df.empty:
        col_f1, col_f2, col_f3 = st.columns(3)
        cat_filtro = col_f1.multiselect("Categoria", options=["Veículo", "Imóvel", "Móveis", "Informática", "Eletrodomésticos"], default=["Veículo", "Imóvel", "Móveis", "Informática", "Eletrodomésticos"])
        stat_filtro = col_f2.multiselect("Status", options=["Disponível", "Em Uso", "Em Manutenção"], default=["Disponível", "Em Uso", "Em Manutenção"])
        loc_filtro = col_f3.multiselect("Localização", options=df["localizacao"].unique(), default=df["localizacao"].unique())

        df_filtrado = df[
            df["categoria"].isin(cat_filtro) & 
            df["status"].isin(stat_filtro) & 
            df["localizacao"].isin(loc_filtro)
        ]

        st.dataframe(df_filtrado, width="stretch")
        csv_data = df_filtrado.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Baixar Relatório Filtrado em CSV", data=csv_data, file_name="relatorio_patrimonio_ispn.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("📜 Histórico Geral de Movimentações")
    st.dataframe(pd.DataFrame(historico_db), width="stretch")
