import streamlit as st
import pandas as pd
from datetime import datetime

def processar_moeda(valor_input):
    """
    Recebe entradas como 1500, 1500.85, 1500,85 ou R$ 1.500,00
    Retorna uma tupla: (texto_formatado_brl, valor_float)
    """
    if valor_input is None or str(valor_input).strip() == "":
        return "", 0.0

    val_str = str(valor_input).replace("R$", "").strip()

    if "," in val_str:
        val_str = val_str.replace(".", "").replace(",", ".")

    try:
        val_float = float(val_str)
        texto_brl = f"R$ {val_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return texto_brl, val_float
    except ValueError:
        return str(valor_input), 0.0

def resetar_campos_callback():
    """Limpa os campos de forma segura ANTES de renderizá-los novamente."""
    st.session_state["input_numero_nf"] = ""
    st.session_state["input_nome_fornecedor"] = ""
    st.session_state["campo_valor_raw"] = ""
    st.session_state["input_etiqueta"] = ""
    st.session_state["input_nome"] = ""
    st.session_state["input_setor"] = ""
    st.session_state["input_responsavel"] = "Equipe ISPN"
    st.session_state["input_placa"] = ""
    st.session_state["input_observacoes"] = ""
    if "input_arquivo_nf" in st.session_state:
        del st.session_state["input_arquivo_nf"]

def render_gestao(patrimonio_db, historico_db, cidades_db=None, save_callback=None):
    
    # Inicializa estado das chaves de input se não existirem
    if "campo_valor_raw" not in st.session_state:
        st.session_state["campo_valor_raw"] = ""
    if "input_numero_nf" not in st.session_state:
        st.session_state["input_numero_nf"] = ""
    if "input_nome_fornecedor" not in st.session_state:
        st.session_state["input_nome_fornecedor"] = ""

    # --- FORMULÁRIO ABERTO POR PADRÃO ---
    with st.expander("Cadastrar Novo Patrimônio", expanded=True):
        
        with st.form("form_cadastro_patrimonio"):
            st.markdown("### Dados da Nota Fiscal / Compra")
            col_nf1, col_nf2, col_nf3 = st.columns([1, 2, 1.5])
            
            with col_nf1:
                numero_nf = st.text_input("Nº NF", key="input_numero_nf")
            with col_nf2:
                fornecedor = st.text_input("Nome do Fornecedor", key="input_nome_fornecedor")
            with col_nf3:
                valor_raw = st.text_input(
                    "Valor Unitário do Bem (R$)",
                    key="campo_valor_raw",
                    placeholder="Ex: 1500 ou 1500,85",
                    help="Digite o valor (Ex: 1500 ou 1500,85)"
                )

            arquivo_nf = st.file_uploader(
                "Upload da NOTA FISCAL (PDF/Imagem)", 
                type=["pdf", "png", "jpg", "jpeg"],
                help="Selecione o arquivo da Nota Fiscal (máx. 200MB)",
                key="input_arquivo_nf"
            )

            st.markdown("---")
            st.markdown("### Detalhes do Patrimônio")

            col_pat1, col_pat2 = st.columns(2)
            
            locais = cidades_db.get("lista", ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]) if isinstance(cidades_db, dict) else ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]

            with col_pat1:
                etiqueta = st.text_input("Patrimônio (Código/Etiqueta) *", key="input_etiqueta")
                nome = st.text_input("Descrição do bem *", key="input_nome")
                categoria = st.selectbox(
                    "Categoria do bem", 
                    ["Informática", "Mobiliário", "Veículos", "Eletrodomésticos", "Outros"],
                    key="input_categoria"
                )
                setor = st.text_input("Setor", key="input_setor")

            with col_pat2:
                localizacao = st.selectbox("Localização / Cidade", locais, key="input_localizacao")
                responsavel = st.text_input("Responsável", key="input_responsavel")
                estado = st.selectbox("Situação / Status", ["Em Uso", "Em Manutenção", "Inservível", "Baixado"], key="input_estado")
                placa = st.text_input("Placa (Se Veículo)", key="input_placa")

            observacoes = st.text_area("Observações", key="input_observacoes")

            # O resetar_campos_callback é chamado via on_click com segurança no ciclo do formulário
            submitted = st.form_submit_button("Cadastrar Patrimônio", type="primary", use_container_width=True)
            
            if submitted:
                if not etiqueta or not nome:
                    st.error("Preencha os campos obrigatórios (*): Código/Etiqueta e Descrição do bem.")
                else:
                    etiqueta_existe = any(str(item.get("etiqueta", "")).strip() == etiqueta.strip() for item in patrimonio_db)
                    if etiqueta_existe:
                        st.error(f"Já existe um patrimônio cadastrado com a etiqueta '{etiqueta}'.")
                    else:
                        _, valor_unitario = processar_moeda(valor_raw)
                        
                        nf_dados = None
                        if arquivo_nf is not None:
                            nf_dados = {
                                "nome_arquivo": arquivo_nf.name,
                                "conteudo": arquivo_nf.getvalue(),
                                "tipo": arquivo_nf.type
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
                        
                        historico_db.append({
                            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "usuario": st.session_state.get("username", "Sistema"),
                            "acao": "Cadastro",
                            "etiqueta": etiqueta.strip(),
                            "detalhes": f"Patrimônio '{nome.strip()}' cadastrado com sucesso."
                        })

                        if save_callback:
                            save_callback()
                            
                        # Limpa os valores para o próximo ciclo
                        resetar_campos_callback()
                        st.toast(f"Patrimônio '{nome}' cadastrado com sucesso!", icon="✅")
                        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- LISTAGEM E TABELA DE PATRIMÔNIOS ---
    if not patrimonio_db:
        st.info("Nenhum patrimônio cadastrado até o momento.")
        return

    dados_tabela = []
    for item in patrimonio_db:
        item_copia = item.copy()
        if isinstance(item_copia.get("arquivo_nf"), dict):
            item_copia["arquivo_nf"] = item_copia["arquivo_nf"].get("nome_arquivo", "Anexado")
        else:
            item_copia["arquivo_nf"] = "Não anexado"
        dados_tabela.append(item_copia)

    df = pd.DataFrame(dados_tabela)

    col_busca, col_filtro_cat = st.columns([2, 1])
    with col_busca:
        busca = st.text_input("Pesquisar por Etiqueta, Nome ou Responsável:")
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

    st.subheader(f"Itens Cadastrados ({len(df_filtrado)})")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    # --- PAINEL DE NOTAS FISCAIS E DETALHES DOS BENS ---
    with st.expander(" Visualizar Notas Fiscais e Detalhes dos Itens", expanded=False):
        for idx, item in enumerate(patrimonio_db):
            etiqueta_item = item.get("etiqueta", "N/A")
            nome_item = item.get("nome", "Item sem nome")
            
            with st.container(border=True):
                c_det, c_arquivo = st.columns([2, 1])
                
                with c_det:
                    st.markdown(f"#### 📌 `{etiqueta_item}` - {nome_item}")
                    st.write(f"**Fornecedor:** {item.get('fornecedor', '-')} | **Nº NF:** {item.get('numero_nf', '-')}")
                    st.write(f"**Valor:** R$ {float(item.get('valor_unitario', 0.0)):,.2f} | **Localização:** {item.get('localizacao', '-')}")
                    st.write(f"**Responsável:** {item.get('responsavel', '-')} | **Status:** {item.get('estado', '-')}")
                    
                with c_arquivo:
                    nf_info = item.get("arquivo_nf")
                    if isinstance(nf_info, dict) and "conteudo" in nf_info:
                        nome_arq = nf_info.get("nome_arquivo", "nota_fiscal")
                        conteudo_bytes = nf_info.get("conteudo")
                        mime_tipo = nf_info.get("tipo", "application/pdf")
                        
                        st.download_button(
                            label=f"⬇️ Baixar NF ({nome_arq})",
                            data=conteudo_bytes,
                            file_name=nome_arq,
                            mime=mime_tipo,
                            key=f"dl_nf_list_{etiqueta_item}_{idx}"
                        )
                        
                        if any(nome_arq.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                            st.image(conteudo_bytes, caption=f"NF: {nome_arq}", use_container_width=True)
                        else:
                            st.caption(" Documento em PDF disponível para download.")
                    else:
                        st.caption("⚠️ Nenhuma Nota Fiscal anexada para este item.")

    # --- SEÇÃO DE EDIÇÃO E REMOÇÃO ---
    with st.expander("Editar ou Remover Patrimônio", expanded=False):
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
                        
                        val_atual = item_obj.get("valor_unitario", item_obj.get("valor", 0.0))
                        val_str_inicial, _ = processar_moeda(val_atual)
                        
                        e_val_raw = st.text_input("Valor Unitário (R$)", value=val_str_inicial)
                        e_val_txt, e_val_float = processar_moeda(e_val_raw)
                        
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
                            patrimonio_db[idx_item]["valor_unitario"] = e_val_float
                            
                            if e_arquivo is not None:
                                patrimonio_db[idx_item]["arquivo_nf"] = {
                                    "nome_arquivo": e_arquivo.name,
                                    "conteudo": e_arquivo.getvalue(),
                                    "tipo": e_arquivo.type
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
                    if st.button(f"Excluir {item_sel_cod}", type="secondary", use_container_width=True):
                        patrimonio_db.pop(idx_item)
                        if save_callback:
                            save_callback()
                        st.success("Item excluído com sucesso!")
                        st.rerun()
