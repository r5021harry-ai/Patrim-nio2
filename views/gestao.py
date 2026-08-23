import streamlit as st
import pandas as pd
from services.patrimonio import add_patrimonio, update_patrimonio, delete_patrimonio

def render_gestao(patrimonio_db, historico_db, cidades_db):
    st.markdown("<h2 style='color: #1b4332;'>📦 Gestão de Bens Patrimoniais</h2>", unsafe_allow_html=True)
    df = pd.DataFrame(patrimonio_db)
    
    lista_cidades = cidades_db.get("lista", ["Santa Inês – MA"])
    cidade_padrao = cidades_db.get("padrao", "Santa Inês – MA")
    idx_padrao = lista_cidades.index(cidade_padrao) if cidade_padrao in lista_cidades else 0

    # Cria a terceira aba de exclusão apenas para Administradores
    if st.session_state.get("role") == "admin":
        tab1, tab2, tab3 = st.tabs(["➕ Novo Item", "✏️ Editar Item", "🗑️ Excluir Item (Admin)"])
    else:
        tab1, tab2 = st.tabs(["➕ Novo Item", "✏️ Editar Item"])
        tab3 = None

    with tab1:
        st.subheader("➕ Cadastrar Novo Item")
        with st.form("form_novo"):
            etiq = st.text_input("Código / Etiqueta", value=f"PAT-00{len(patrimonio_db)+1}")
            nome = st.text_input("Nome do Bem")
            cat = st.selectbox("Categoria", ["Veículo", "Imóvel", "Móveis", "Informática", "Eletrodomésticos"])
            loc = st.selectbox("Cidade / Filial", options=lista_cidades, index=idx_padrao)
            stat = st.selectbox("Status Inicial", ["Disponível", "Em Uso", "Em Manutenção"])
            resp = st.text_input("Responsável Inicial", value="Equipe ISPN")
            
            if st.form_submit_button("Cadastrar Patrimônio", use_container_width=True):
                if etiq and nome:
                    ok, msg = add_patrimonio(patrimonio_db, historico_db, etiq, nome, cat, loc, stat, resp)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Preencha a etiqueta e o nome do bem.")

    with tab2:
        st.subheader("✏️ Editar Item Existente")
        if not df.empty:
            item_sel = st.selectbox("Selecione o Item para Editar", [f"{i['etiqueta']} - {i['nome']}" for i in patrimonio_db], key="sel_edit")
            etiq_edit = item_sel.split(" - ")[0]
            item_obj = next(i for i in patrimonio_db if i["etiqueta"] == etiq_edit)
            
            with st.form("form_edit"):
                e_nome = st.text_input("Nome", value=item_obj["nome"])
                e_cat = st.selectbox("Categoria", ["Veículo", "Imóvel", "Móveis", "Informática", "Eletrodomésticos"], index=["Veículo", "Imóvel", "Móveis", "Informática", "Eletrodomésticos"].index(item_obj["categoria"]))
                
                loc_idx = lista_cidades.index(item_obj["localizacao"]) if item_obj["localizacao"] in lista_cidades else 0
                e_loc = st.selectbox("Cidade / Filial", options=lista_cidades, index=loc_idx)
                
                e_stat = st.selectbox("Status", ["Disponível", "Em Uso", "Em Manutenção"], index=["Disponível", "Em Uso", "Em Manutenção"].index(item_obj["status"]))
                e_resp = st.text_input("Responsável", value=item_obj["responsavel"])
                
                if st.form_submit_button("Salvar Alterações", use_container_width=True):
                    ok, msg = update_patrimonio(patrimonio_db, etiq_edit, e_nome, e_cat, e_loc, e_stat, e_resp)
                    if ok:
                        st.success(msg)
                        st.rerun()
        else:
            st.info("Nenhum item disponível para edição.")

    if tab3:
        with tab3:
            st.subheader("🗑️ Remover Patrimônio do Sistema")
            st.warning("⚠️ Atenção: Esta ação é irreversível e excluirá o bem permanentemente da base.")
            if not df.empty:
                item_del_sel = st.selectbox("Selecione o Item para Excluir", [f"{i['etiqueta']} - {i['nome']} ({i['localizacao']})" for i in patrimonio_db], key="sel_del")
                etiq_del = item_del_sel.split(" - ")[0]
                
                if st.button("🔴 Confirmar Exclusão Permanente", use_container_width=True):
                    ok, msg = delete_patrimonio(patrimonio_db, historico_db, etiq_del)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                st.info("Nenhum item disponível para exclusão.")
