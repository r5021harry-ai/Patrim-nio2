import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

DATA_DIR = "data"
ANEXOS_DIR = os.path.join(DATA_DIR, "anexos_nf")
os.makedirs(ANEXOS_DIR, exist_ok=True)

# Mapeamento Oficial de Colunas da Planilha
COLUNAS_OFICIAIS = [
    "Patrimônio", "Ano", "Data de Emissão NF", "Nº NF", "Quant.", "Fornecedor",
    "Descrição do bem", "Categoria do bem", "Valor do bem", "Valor registrado no laudo",
    "Valor atualizado (depreciado)", "Projeto", "Status do projeto", "Localização no escritório",
    "Responsável", "Setor", "Situação", "TERMO DE ENTREGA", "TERMOS DE DEVOLUÇÃO",
    "TERMOS DE DOAÇÃO", "Última conferência", "NOTA FISCAL", "FOTO", "Observações"
]

def salvar_anexo(file_upload, subpasta="anexos_nf"):
    """Salva arquivos na pasta nativa data/"""
    if file_upload is None:
        return ""
    caminho_dir = os.path.join(DATA_DIR, subpasta)
    os.makedirs(caminho_dir, exist_ok=True)
    
    nome_arquivo = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_upload.name}"
    caminho_completo = os.path.join(caminho_dir, nome_arquivo)
    
    with open(caminho_completo, "wb") as f:
        f.write(file_upload.getbuffer())
    return caminho_completo

def render_cadastro(patrimonio_db, save_callback=None):
    st.title("➕ Cadastro e Importação de Patrimônio")
    
    tab1, tab2 = st.tabs(["📝 Lançamento Individual / Nota Fiscal", "📥 Importação em Lote (Planilha)"])

    # --- TAB 1: CADASTRO COM NOTA FISCAL (MULTI-LANÇAMENTO) ---
    with tab1:
        st.subheader("📄 Dados da Nota Fiscal / Compra")
        
        with st.form("form_nf_patrimonio"):
            col_nf1, col_nf2, col_nf3 = st.columns(3)
            with col_nf1:
                num_nf = st.text_input("Nº da Nota Fiscal *")
                data_emissao_nf = st.date_input("Data de Emissão da NF")
                fornecedor = st.text_input("Fornecedor / Razão Social")
            
            with col_nf2:
                ano_compra = st.number_input("Ano da Compra", min_value=1990, max_value=2030, value=datetime.now().year)
                qtd_itens_nf = st.number_input("Qtd. de Itens na mesma NF", min_value=1, max_value=50, value=1)
                projeto = st.text_input("Projeto")
            
            with col_nf3:
                status_projeto = st.selectbox("Status do Projeto", ["Ativo", "Encerrado", "Pendente"])
                anexo_nf = st.file_uploader("Upload da Nota Fiscal (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"])

            st.divider()
            st.subheader("📦 Detalhes do Patrimônio")

            col_item1, col_item2, col_item3 = st.columns(3)
            with col_item1:
                cod_patrimonio = st.text_input("Código do Patrimônio (Etiqueta) *")
                descricao_bem = st.text_input("Descrição do Bem *")
                categoria = st.selectbox("Categoria", ["Informática", "Mobiliário", "Veículos", "Eletroeletrônicos", "Outros"])
                setor = st.text_input("Setor")

            with col_item2:
                valor_bem = st.number_input("Valor do Bem (R$)", min_value=0.0, format="%.2f")
                valor_laudo = st.number_input("Valor Registrado no Laudo (R$)", min_value=0.0, format="%.2f")
                valor_depreciado = st.number_input("Valor Atualizado / Depreciado (R$)", min_value=0.0, format="%.2f")
                situacao = st.selectbox("Situação", ["Em Uso", "Disponível", "Manutenção", "Baixado", "Doado"])

            with col_item3:
                localizacao = st.text_input("Localização no Escritório")
                responsavel = st.text_input("Responsável")
                foto_bem = st.file_uploader("Foto do Bem (Opcional)", type=["png", "jpg", "jpeg"])
                obs = st.text_area("Observações")

            submit = st.form_submit_button("🚀 Cadastrar Patrimônio", type="primary", use_container_width=True)

            if submit:
                if not cod_patrimonio or not descricao_bem:
                    st.error("Preencha ao menos o Código do Patrimônio e a Descrição do Bem.")
                else:
                    caminho_nf = salvar_anexo(anexo_nf, "anexos_nf")
                    caminho_foto = salvar_anexo(foto_bem, "fotos_bens")

                    novo_registro = {
                        "Patrimônio": cod_patrimonio,
                        "Ano": ano_compra,
                        "Data de Emissão NF": str(data_emissao_nf),
                        "Nº NF": num_nf,
                        "Quant.": qtd_itens_nf,
                        "Fornecedor": fornecedor,
                        "Descrição do bem": descricao_bem,
                        "Categoria do bem": categoria,
                        "Valor do bem": valor_bem,
                        "Valor registrado no laudo": valor_laudo,
                        "Valor atualizado (depreciado)": valor_depreciado,
                        "Projeto": projeto,
                        "Status do projeto": status_projeto,
                        "Localização no escritório": localizacao,
                        "Responsável": responsavel,
                        "Setor": setor,
                        "Situação": situacao,
                        "TERMO DE ENTREGA": "",
                        "TERMOS DE DEVOLUÇÃO": "",
                        "TERMOS DE DOAÇÃO": "",
                        "Última conferência": "",
                        "NOTA FISCAL": caminho_nf,
                        "FOTO": caminho_foto,
                        "Observações": obs
                    }

                    patrimonio_db.append(novo_registro)

                    # Salva nativamente na pasta data/patrimonio.csv
                    df_salvar = pd.DataFrame(patrimonio_db)
                    df_salvar.to_csv(os.path.join(DATA_DIR, "patrimonio.csv"), index=False)

                    if save_callback:
                        save_callback()

                    st.success(f"Patrimônio **{cod_patrimonio}** cadastrado com sucesso e vinculado à NF **{num_nf}**!")

    # --- TAB 2: IMPORTAÇÃO DA PLANILHA DO INSTITUTO ---
    with tab2:
        st.subheader("📥 Importar Planilha Existente")
        st.caption("O arquivo deve conter as colunas do modelo oficial do instituto.")

        arquivo_excel = st.file_uploader("Selecione o arquivo Excel (.xlsx) ou CSV", type=["xlsx", "xls", "csv"])

        if arquivo_excel:
            try:
                if arquivo_excel.name.endswith(".csv"):
                    df_imp = pd.read_csv(arquivo_excel)
                else:
                    df_imp = pd.read_excel(arquivo_excel)

                st.markdown("**Pré-visualização dos dados importados:**")
                st.dataframe(df_imp.head(5), use_container_width=True)

                if st.button("Confirmar Importação de Todos os Dados", type="primary"):
                    novos_dados = df_imp.to_dict(orient="records")
                    patrimonio_db.extend(novos_dados)

                    # Atualiza arquivo local na pasta data/
                    df_total = pd.DataFrame(patrimonio_db)
                    df_total.to_csv(os.path.join(DATA_DIR, "patrimonio.csv"), index=False)

                    if save_callback:
                        save_callback()

                    st.success(f"{len(novos_dados)} registros importados com sucesso para a pasta nativa do app!")
            except Exception as e:
                st.error(f"Erro ao processar o arquivo: {e}")
