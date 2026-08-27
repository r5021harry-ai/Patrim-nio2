import streamlit as st
import pandas as pd
from datetime import datetime

def render_conferencia(patrimonio_db, historico_db, cidades_db=None, save_callback=None):
    st.title("Conferência e Auditoria de Patrimônio")

    if not patrimonio_db:
        st.info("Nenhum patrimônio cadastrado para realizar conferência.")
        return

    df = pd.DataFrame(patrimonio_db)

    col_etiqueta = next((c for c in ['etiqueta', 'patrimonio', 'Etiqueta', 'Patrimônio'] if c in df.columns), df.columns[0])
    col_nome = next((c for c in ['nome', 'item', 'descricao', 'Nome', 'Item', 'Descrição'] if c in df.columns), df.columns[1] if len(df.columns) > 1 else col_etiqueta)
    col_local = next((c for c in ['localizacao', 'cidade', 'Localização', 'Cidade'] if c in df.columns), None)
    col_status = next((c for c in ['status', 'estado', 'Status', 'Estado'] if c in df.columns), None)
    col_resp = next((c for c in ['responsavel', 'Responsável'] if c in df.columns), None)

    lista_locais = []
    if cidades_db and isinstance(cidades_db, dict) and "lista" in cidades_db:
        lista_locais = cidades_db["lista"]
    elif col_local and col_local in df.columns:
        lista_locais = sorted(df[col_local].dropna().astype(str).unique().tolist())
    
    if not lista_locais:
        lista_locais = ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]

    st.markdown("**Selecione o Local para Auditoria**")
    local_selecionado = st.selectbox("Localização:", lista_locais, label_visibility="collapsed")

    if col_local in df.columns:
        df_local = df[df[col_local].astype(str) == str(local_selecionado)]
    else:
        df_local = df.copy()

    st.markdown("---")

    col_m1, col_m2, col_m3 = st.columns(3)
    total_local = len(df_local)
    col_m1.metric("Total no Local", total_local)
    
    if "auditados" not in st.session_state:
        st.session_state.auditados = set()

    auditados_no_local = [etq for etq in st.session_state.auditados if etq in df_local[col_etiqueta].astype(str).values]
    
    col_m2.metric("Conferidos", len(auditados_no_local))
    col_m3.metric("Pendentes", total_local - len(auditados_no_local))

    st.markdown("---")

    tab_bipar, tab_lista = st.tabs(["Leitura / Bipagem de Etiquetas", "Lista de Verificação (Checklist)"])

    with tab_bipar:
        st.markdown("**Registro Rápido de Leitura (Código de Barras / Etiqueta)**")
        
        with st.form("form_bipagem", clear_on_submit=True):
            codigo_input = st.text_input("Digite ou bipe a etiqueta do bem:", placeholder="Ex: PAT001").strip()
            submitted = st.form_submit_button("Confirmar Leitura", type="primary")

            if submitted and codigo_input:
                item_match = df[df[col_etiqueta].astype(str).str.lower() == codigo_input.lower()]

                if item_match.empty:
                    st.error(f"Etiqueta '{codigo_input}' não encontrada no sistema.")
                else:
                    item_info = item_match.iloc[0]
                    etiqueta_real = str(item_info[col_etiqueta])
                    local_atual_item = str(item_info[col_local]) if col_local else "Não informado"

                    st.session_state.auditados.add(etiqueta_real)

                    novo_evento = {
                        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "usuario": st.session_state.get("username", "Sistema"),
                        "acao": "Conferência / Auditoria",
                        "etiqueta": etiqueta_real,
                        "detalhes": f"Item conferido em '{local_selecionado}' (Local cadastrado: '{local_atual_item}')"
                    }
                    historico_db.append(novo_evento)

                    if save_callback:
                        save_callback()

                    if local_atual_item == str(local_selecionado):
                        st.success(f"Item '{item_info[col_nome]}' ({etiqueta_real}) verificado com sucesso!")
                    else:
                        st.warning(f"Item '{item_info[col_nome]}' ({etiqueta_real}) verificado, porém consta cadastrado em '{local_atual_item}'.")

    with tab_lista:
        st.markdown(f"**Itens Cadastrados em: {local_selecionado}**")
        
        if df_local.empty:
            st.info("Nenhum bem cadastrado nesta localização.")
        else:
            df_display = df_local.copy()
            df_display["Status Conferência"] = df_display[col_etiqueta].astype(str).apply(
                lambda x: "Conferido" if x in st.session_state.auditados else "Pendente"
            )

            cols_exibicao = [col_etiqueta, col_nome, "Status Conferência"]
            if col_status and col_status in df_display.columns:
                cols_exibicao.append(col_status)
            if col_resp and col_resp in df_display.columns:
                cols_exibicao.append(col_resp)

            st.dataframe(df_display[cols_exibicao], use_container_width=True, hide_index=True)

            if st.button("Limpar Auditoria Atual", type="primary"):
                st.session_state.auditados = set()
                st.rerun()
