import streamlit as st
import pandas as pd

def render_conferencia(patrimonio_db, historico_db, cidades_db=None, save_callback=None):
    st.subheader("Conferência / Auditoria de Patrimônio")

    # --- SELEÇÃO DE LOCALIZAÇÃO ---
    locais = cidades_db.get("lista", ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]) if isinstance(cidades_db, dict) else ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]
    
    local_selecionado = st.selectbox("Selecione o Local para Auditoria", locais, key="conf_local_sel")

    # Filtrar itens do local selecionado
    itens_do_local = [item for item in patrimonio_db if item.get("localizacao") == local_selecionado]
    
    # Gerenciamento do estado da sessão para itens conferidos
    if "conferidos" not in st.session_state:
        st.session_state.conferidos = set()

    total_local = len(itens_do_local)
    conferidos_local = sum(1 for item in itens_do_local if item.get("etiqueta") in st.session_state.conferidos)
    pendentes_local = total_local - conferidos_local

    # --- CARDS DE MÉTRICAS ---
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total no Local", total_local)
    with c2:
        st.metric("Conferidos", conferidos_local)
    with c3:
        st.metric("Pendentes", pendentes_local)

    st.markdown("---")

    # --- ABAS DE LEITURA E CHECKLIST ---
    aba_leitura, aba_checklist = st.tabs(["Leitura / Bipagem de Etiquetas", "Lista de Verificação (Checklist)"])

    with aba_leitura:
        st.markdown("### Registro Rápido de Leitura (Código de Barras / Etiqueta)")
        
        # Prepara a lista pesquisável de todos os itens ou apenas do local
        if patrimonio_db:
            # Cria a lista formatada: "CÓDIGO - NOME (LOCAL)"
            opcoes_itens = [""] + [
                f"{item.get('etiqueta', '')} - {item.get('nome', '')} ({item.get('localizacao', '')})"
                for item in patrimonio_db
            ]
        else:
            opcoes_itens = ["Nenhum item cadastrado"]

        with st.form("form_bipagem_conferencia", clear_on_submit=True):
            # Substituído st.text_input por st.selectbox com busca ativada
            item_selecionado = st.selectbox(
                "Selecione ou pesquise a etiqueta/nome do bem:",
                options=opcoes_itens,
                index=0,
                help="Digite o código ou o nome do bem para filtrar na lista."
            )
            
            submitted = st.form_submit_button("Confirmar Leitura", type="primary")

            if submitted:
                if item_selecionado and item_selecionado != "Nenhum item cadastrado":
                    # Extrai apenas o código da etiqueta (parte antes do ' - ')
                    etiqueta_bipada = item_selecionado.split(" - ")[0].strip()
                    
                    # Verifica se o código existe no banco geral
                    item_encontrado = next((i for i in patrimonio_db if str(i.get("etiqueta")).strip() == etiqueta_bipada), None)

                    if item_encontrado:
                        st.session_state.conferidos.add(etiqueta_bipada)
                        
                        if item_encontrado.get("localizacao") == local_selecionado:
                            st.success(f"Item '{item_encontrado.get('nome')}' ({etiqueta_bipada}) conferido com sucesso no local '{local_selecionado}'!")
                        else:
                            st.warning(f"Atenção: O item '{item_encontrado.get('nome')}' ({etiqueta_bipada}) está registrado no local '{item_encontrado.get('localizacao')}', mas foi conferido em '{local_selecionado}'.")
                        
                        st.rerun()
                    else:
                        st.error(f"Etiqueta '{etiqueta_bipada}' não encontrada no sistema.")
                else:
                    st.error("Por favor, selecione um bem válido.")

    with aba_checklist:
        st.markdown(f"### Lista de Bens em **{local_selecionado}**")
        if itens_do_local:
            dados_checklist = []
            for item in itens_do_local:
                etiq = item.get("etiqueta")
                foi_conferido = etiq in st.session_state.conferidos
                dados_checklist.append({
                    "Status": "Conferido" if foi_conferido else "Pendente",
                    "Etiqueta": etiq,
                    "Nome": item.get("nome"),
                    "Categoria": item.get("categoria"),
                    "Responsável": item.get("responsavel"),
                    "Situação": item.get("estado")
                })
            
            df_check = pd.DataFrame(dados_checklist)
            st.dataframe(df_check, use_container_width=True, hide_index=True)
        else:
            st.info(f"Nenhum patrimônio cadastrado para o local '{local_selecionado}'.")
