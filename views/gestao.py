import streamlit as st
import pandas as pd
import importlib

# Tenta carregar a função de salvar dados do banco
try:
    db_mod = importlib.import_module("banco de dados.db")
except ModuleNotFoundError:
    try:
        db_mod = importlib.import_module("banco_dados.db")
    except ModuleNotFoundError:
        db_mod = importlib.import_module("database.db")

save_all_data = getattr(db_mod, "save_all_data", getattr(db_mod, "guardar_todos_os_dados", None))

def render_gestao(patrimonio_db, historico_db, cidades_db=None):
    st.title("📦 Gestão de Bens Patrimoniais")
    
    aba_sub = st.tabs(["➕ Novo Item", "✏️ Editar Item", "🗑️ Excluir Item (Admin)"])
    
    # --- ABA 1: CADASTRAR NOVO ITEM ---
    with aba_sub[0]:
        st.subheader("➕ Cadastrar Novo Item")
        
        cidades_lista = cidades_db.get("lista", ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]) if cidades_db else ["Santa Inês – MA"]
        
        # Sugestão automática de código
        proximo_id = len(patrimonio_db) + 1
        codigo_sugerido = f"PAT-{proximo_id:03d}"

        with st.form("form_cadastrar_item", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                etiqueta = st.text_input("Código / Etiqueta", value=codigo_sugerido)
                nome_bem = st.text_input("Nome do Bem")
                categoria = st.selectbox("Categoria", ["Veículo", "Informática", "Móveis", "Eletrônicos", "Equipamento", "Outros"])
            
            with col2:
                cidade = st.selectbox("Cidade / Filial", cidades_lista)
                status = st.selectbox("Status Inicial", ["Disponível", "Em Uso", "Manutenção", "Baixado"])
                responsavel = st.text_input("Responsável Inicial", value="Equipe ISPN")

            btn_cadastrar = st.form_submit_button("Cadastrar Patrimônio", type="primary", use_container_width=True)

            if btn_cadastrar:
                if not nome_bem.strip():
                    st.warning("⚠️ Por favor, informe o nome do bem.")
                else:
                    # Cria e salva o novo item
                    novo_item = {
                        "etiqueta": etiqueta,
                        "item": nome_bem,
                        "categoria": categoria,
                        "localizacao": cidade,
                        "status": status,
                        "responsavel": responsavel
                    }
                    patrimonio_db.append(novo_item)
                    
                    if save_all_data:
                        try:
                            save_all_data(st.session_state.users_db, patrimonio_db, historico_db, cidades_db)
                        except Exception:
                            pass
                    
                    # NOTIFICAÇÕES DE SUCESSO AO CLICAR EM CADASTRAR
                    st.toast("Feito! Patrimônio cadastrado com sucesso.", icon="🎉")
                    st.success(f"✅ Feito! O item '{nome_bem}' ({etiqueta}) foi cadastrado com sucesso.")

    # --- ABA 2: EDITAR ITEM ---
    with aba_sub[1]:
        st.subheader("✏️ Editar Item Existente")
        df_patrimonio = pd.DataFrame(patrimonio_db)
        if not df_patrimonio.empty:
            col_eq = 'etiqueta' if 'etiqueta' in df_patrimonio.columns else df_patrimonio.columns[0]
            col_nm = 'item' if 'item' in df_patrimonio.columns else df_patrimonio.columns[1]
            
            opcoes = df_patrimonio[col_eq].astype(str) + " - " + df_patrimonio[col_nm].astype(str)
            item_sel = st.selectbox("Selecione para Editar:", opcoes)
            
            if item_sel:
                cod_sel = item_sel.split(" - ")[0]
                idx = next((i for i, item in enumerate(patrimonio_db) if str(item.get(col_eq)) == cod_sel), None)
                
                if idx is not None:
                    dados = patrimonio_db[idx]
                    with st.form("form_editar_item"):
                        e_nome = st.text_input("Nome do Bem", value=dados.get(col_nm, ""))
                        e_cat = st.text_input("Categoria", value=dados.get("categoria", ""))
                        e_loc = st.text_input("Localização", value=dados.get("localizacao", ""))
                        e_status = st.selectbox("Status", ["Disponível", "Em Uso", "Manutenção", "Baixado"], index=0)
                        e_resp = st.text_input("Responsável", value=dados.get("responsavel", ""))
                        
                        if st.form_submit_button("Salvar Alterações", type="primary"):
                            patrimonio_db[idx][col_nm] = e_nome
                            patrimonio_db[idx]["categoria"] = e_cat
                            patrimonio_db[idx]["localizacao"] = e_loc
                            patrimonio_db[idx]["status"] = e_status
                            patrimonio_db[idx]["responsavel"] = e_resp
                            
                            if save_all_data:
                                try: save_all_data(st.session_state.users_db, patrimonio_db, historico_db, cidades_db)
                                except Exception: pass
                                
                            st.toast("Feito! Item atualizado.", icon="✅")
                            st.success("✅ Feito! Alterações salvas com sucesso.")
        else:
            st.info("Nenhum item disponível para edição.")

    # --- ABA 3: EXCLUIR ITEM ---
    with aba_sub[2]:
        st.subheader("🗑️ Excluir Item do Patrimônio")
        if st.session_state.get("role") == "admin":
            df_patrimonio = pd.DataFrame(patrimonio_db)
            if not df_patrimonio.empty:
                col_eq = 'etiqueta' if 'etiqueta' in df_patrimonio.columns else df_patrimonio.columns[0]
                col_nm = 'item' if 'item' in df_patrimonio.columns else df_patrimonio.columns[1]
                
                opcoes_del = df_patrimonio[col_eq].astype(str) + " - " + df_patrimonio[col_nm].astype(str)
                item_del = st.selectbox("Selecione para Excluir:", opcoes_del)
                
                if st.button("🚨 Confirmar Exclusão", type="primary"):
                    cod_del = item_del.split(" - ")[0]
                    patrimonio_db[:] = [item for item in patrimonio_db if str(item.get(col_eq)) != cod_del]
                    
                    if save_all_data:
                        try: save_all_data(st.session_state.users_db, patrimonio_db, historico_db, cidades_db)
                        except Exception: pass
                        
                    st.toast("Item removido!", icon="🗑️")
                    st.success("✅ Feito! Item excluído com sucesso.")
                    st.rerun()
            else:
                st.info("Nenhum item para excluir.")
        else:
            st.warning("Apenas administradores podem excluir itens.")
