import streamlit as st
import pandas as pd

def render_gestao(patrimonio_db, historico_db, cidades_db=None, save_callback=None):
    st.title("📦 Gestão de Patrimônio")
    
    # --- BARRA SUPERIOR DE AÇÕES E CADASTRO ---
    with st.expander("➕ Cadastrar Novo Patrimônio", expanded=False):
        with st.form("form_novo_patrimonio"):
            st.markdown("### 📄 Dados da Nota Fiscal / Compra")
            
            col_nf1, col_nf2, col_nf3 = st.columns([1, 2, 1])
            with col_nf1:
                numero_nf = st.text_input("Nº NF")
            with col_nf2:
                fornecedor = st.text_input("Nome do Fornecedor")
            with col_nf3:
                valor_unitario = st.number_input(
                    "Valor Unitário do Bem (R$)", 
                    value=0.0, 
                    min_value=0.0, 
                    step=10.0,
                    format="%.2f"
                )

            # Campo para envio do arquivo da Nota Fiscal
            arquivo_nf = st.file_uploader(
                "Upload da NOTA FISCAL (PDF/Imagem)", 
                type=["pdf", "png", "jpg", "jpeg"],
                help="Selecione o arquivo da Nota Fiscal (máx. 200MB)"
            )

            st.markdown("---")
            st.markdown("### 📦 Detalhes do Patrimônio")

            col_pat1, col_pat2 = st.columns(2)
            
            locais = cidades_db.get("lista", ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]) if isinstance(cidades_db, dict) else ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]

            with col_pat1:
                etiqueta = st.text_input("Patrimônio (Código/Etiqueta) *")
                nome = st.text_input("Descrição do bem *")
                categoria = st.selectbox(
                    "Categoria do bem", 
                    ["Informática", "Mobiliário", "Veículos", "Eletrodomésticos", "Outros"]
                )
                setor = st.text_input("Setor")

            with col_pat2:
                localizacao = st.selectbox("Localização / Cidade", locais)
                responsavel = st.text_input("Responsável", value="Equipe ISPN")
                estado = st.selectbox("Situação / Status", ["Em Uso", "Em Manutenção", "Inservível", "Baixado"])
                placa = st.text_input("Placa (Se Veículo)")

            observacoes = st.text_area("Observações")

            submitted = st.form_submit_button("Cadastrar Patrimônio", type="primary", use_container_width=True)
            
            if submitted:
                if not etiqueta or not nome:
                    st.error("Preencha os campos obrigatórios (*): Código/Etiqueta e Descrição do bem.")
                else:
                    etiqueta_existe = any(str(item.get("etiqueta", "")).strip() == etiqueta.strip() for item in patrimonio_db)
                    if etiqueta_existe:
                        st.error(f"Já existe um patrimônio cadastrado com a etiqueta '{etiqueta}'.")
                    else:
                        # Dados do arquivo enviado
                        nf_dados = None
                        if arquivo_nf is not None:
                            nf_dados = {
                                "nome_arquivo": arquivo_nf.name,
                                "conteudo": arquivo_nf.getvalue()
                            }

                        novo_item = {
                            "etiqueta": etiqueta.strip(),
                            "nome": nome.strip(),
                            "categoria": categoria,
                            "setor": setor,
                            "numero_nf": numero_nf,
                            "fornecedor": fornecedor,
                            "valor_unitario": valor_unitario,
                            "arquivo_nf": nf_dados,
                            "localizacao": localizacao,
                            "responsavel": responsavel,
                            "estado": estado,
                            "placa": placa,
                            "observacoes": observacoes
                        }
                        
                        patrimonio_db.append(novo_item)
                        
                        if save_callback:
                            save_callback()
                            
                        st.success(f"Patrimônio '{nome}' cadastrado com sucesso!")
                        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- LISTAGEM E TABELA DE PATRIMÔNIOS ---
    if not patrimonio_db:
        st.info("Nenhum patrimônio cadastrado até o momento.")
        return

    # Tratamento para exibição na tabela (remove bytes brutos do DataFrame)
    dados_tabela = []
    for item in patrimonio_db:
        item_copia = item.copy()
        if isinstance(item_copia.get("arquivo_nf"), dict):
            item_copia["arquivo_nf"] = item_copia["arquivo_nf"].get("nome_arquivo", "Anexado")
        dados_tabela.append(item_copia)

    df = pd.DataFrame(dados_tabela)

    col_busca, col_filtro_cat = st.columns([2, 1])
    with col_busca:
        busca = st.text_input("🔍 Pesquisar por Etiqueta, Nome ou Responsável:")
    with col_filtro_cat:
        categorias = ["Todas"] + list(df['categoria'].dropna().unique()) if 'categoria' in df.columns else ["Todas"]
        cat_sel = st.selectbox("Filtrar Categoria:", categorias)

    df_filtrado = df.copy()

    if cat_sel != "Todas" and 'categoria' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['categoria'] == cat_sel]

    if busca:
        mask = (
            df_filtrado.astype(str).apply(lambda row: row.str.contains(busca, case=False, na=False)).any(axis=1)
        )
        df_filtrado = df_filtrado[mask]

    st.subheader(f"📋 Itens Cadastrados ({len(df_filtrado)})")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    # --- SEÇÃO DE EDICÃO E REMOÇÃO ---
    with st.expander("🛠️ Editar ou Remover Patrimônio", expanded=False):
        codigos_disponiveis = [str(item.get("etiqueta")) for item in patrimonio_db if "etiqueta" in item]
        
        if codigos_disponiveis:
            item_sel_cod = st.selectbox("Selecione o Patrimônio pelo código/etiqueta:", codigos_disponiveis)
            
            idx_item = next((i for i, item in enumerate(patrimonio_db) if str(item.get("etiqueta")) == item_sel_cod), None)

            if idx_item is not None:
                item_obj = patrimonio_db[idx_item]
                
                c_edit, c_del = st.columns([3, 1])
                
                with c_edit:
                    with st.form(f"form_edicao_{item_sel_cod}"):
                        st.markdown(f"**Editando:** `{item_sel_cod}`")
                        
                        e_nf = st.text_input("Nº NF", value=item_obj.get("numero_nf", ""))
                        e_forn = st.text_input("Fornecedor", value=item_obj.get("fornecedor", ""))
                        e_val = st.number_input(
                            "Valor Unitário (R$)", 
                            value=float(item_obj.get("valor_unitario", item_obj.get("valor", 0.0))), 
                            format="%.2f"
                        )
                        e_arquivo = st.file_uploader("Substituir Nota Fiscal (PDF/Imagem)", type=["pdf", "png", "jpg", "jpeg"])
                        
                        e_nome = st.text_input("Nome do bem", value=item_obj.get("nome", ""))
                        e_resp = st.text_input("Responsável", value=item_obj.get("responsavel", ""))
                        e_estado = st.selectbox(
                            "Situação", 
                            ["Em Uso", "Em Manutenção", "Inservível", "Baixado"],
                            index=["Em Uso", "Em Manutenção", "Inservível", "Baixado"].index(item_obj.get("estado", "Em Uso")) if item_obj.get("estado") in ["Em Uso", "Em Manutenção", "Inservível", "Baixado"] else 0
                        )

                        if st.form_submit_button("Salvar Alterações", type="primary"):
                            patrimonio_db[idx_item]["numero_nf"] = e_nf
                            patrimonio_db[idx_item]["fornecedor"] = e_forn
                            patrimonio_db[idx_item]["valor_unitario"] = e_val
                            
                            if e_arquivo is not None:
                                patrimonio_db[idx_item]["arquivo_nf"] = {
                                    "nome_arquivo": e_arquivo.name,
                                    "conteudo": e_arquivo.getvalue()
                                }

                            patrimonio_db[idx_item]["nome"] = e_nome
                            patrimonio_db[idx_item]["responsavel"] = e_resp
                            patrimonio_db[idx_item]["estado"] = e_estado

                            if save_callback:
                                save_callback()

                            st.success("Patrimônio atualizado com sucesso!")
                            st.rerun()

                with c_del:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    if st.button(f"🗑️ Excluir {item_sel_cod}", type="secondary", use_container_width=True):
                        patrimonio_db.pop(idx_item)
                        if save_callback:
                            save_callback()
                        st.success("Item excluído com sucesso!")
                        st.rerun()
