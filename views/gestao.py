import streamlit as st
import pandas as pd
from services.patrimonio import add_patrimonio, update_patrimonio

def render_gestao(patrimonio_db, historico_db):
    st.title("📦 Gestão de Bens Patrimoniais")
    df = pd.DataFrame(patrimonio_db)
    c_novo, c_editar = st.columns([1, 1])
    
    with c_novo:
        st.subheader("➕ Cadastrar Novo Item")
        with st.form("form_novo"):
            etiq = st.text_input("Código/Etiqueta", value=f"PAT-00{len(patrimonio_db)+1}")
            nome = st.text_input("Nome do Bem")
            cat = st.selectbox("Categoria ISPN", ["Veículo", "Imóvel", "Móveis", "Informática", "Eletrodomésticos"])
            loc = st.selectbox("Localização Inicial", ["Sede DF", "Campo - Cerrado", "Almoxarifado", "Outro"])
            stat = st.selectbox("Status Inicial", ["Disponível", "Em Uso", "Em Manutenção"])
            resp = st.text_input("Responsável Inicial", value="Nenhum")
            
            if st.form_submit_button("Cadastrar Patrimônio", width="stretch"):
                if etiq and nome:
                    ok, msg = add_patrimonio(patrimonio_db, historico_db, etiq, nome, cat, loc, stat, resp)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Preencha etiqueta e nome.")

    with c_editar:
        st.subheader("✏️ Editar Item Existente")
        if not df.empty:
            item_sel = st.selectbox("Selecione o Item", [f"{i['etiqueta']} - {i['nome']}" for i in patrimonio_db])
            etiq_edit = item_sel.split(" - ")[0]
            item_obj = next(i for i in patrimonio_db if i["etiqueta"] == etiq_edit)
            
            with st.form("form_edit"):
                e_nome = st.text_input("Nome", value=item_obj["nome"])
                e_cat = st.selectbox("Categoria", ["Veículo", "Imóvel", "Móveis", "Informática", "Eletrodomésticos"], index=["Veículo", "Imóvel", "Móveis", "Informática", "Eletrodomésticos"].index(item_obj["categoria"]))
                e_loc = st.text_input("Localização", value=item_obj["localizacao"])
                e_stat = st.selectbox("Status", ["Disponível", "Em Uso", "Em Manutenção"], index=["Disponível", "Em Uso", "Em Manutenção"].index(item_obj["status"]))
                e_resp = st.text_input("Responsável", value=item_obj["responsavel"])
                
                if st.form_submit_button("Salvar Alterações", width="stretch"):
                    ok, msg = update_patrimonio(patrimonio_db, etiq_edit, e_nome, e_cat, e_loc, e_stat, e_resp)
                    if ok:
                        st.success(msg)
                        st.rerun()
        else:
            st.info("Nenhum item para editar.")
