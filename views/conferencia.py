import streamlit as st
import pandas as pd
import io

def gerar_relatorio_txt_pdf(itens_auditados, filtro_categoria="Todas"):
    """
    Gera um relatório formatado em texto/HTML pronto para impressão ou download.
    """
    conteudo = f"RELATÓRIO DE AUDITORIA E VISTORIA DE PATRIMÔNIO\n"
    conteudo += f"Filtro Categoria: {filtro_categoria}\n"
    conteudo += "="*60 + "\n\n"
    
    for idx, item in enumerate(itens_auditados, 1):
        conteudo += f"Item {idx}: {item.get('nome', 'N/A')}\n"
        conteudo += f"  - Etiqueta: {item.get('etiqueta', 'N/A')}\n"
        conteudo += f"  - Localização: {item.get('localizacao', 'N/A')}\n"
        conteudo += f"  - Categoria: {item.get('categoria', 'N/A')}\n"
        conteudo += f"  - Condição/Status: {item.get('estado', 'N/A')}\n"
        conteudo += f"  - Responsável: {item.get('responsavel', 'N/A')}\n"
        conteudo += f"  - Obs. Vistoria: {item.get('obs_vistoria', 'Sem observações')}\n"
        conteudo += f"  - Fotos Anexadas: {item.get('qtd_fotos', 0)} foto(s)\n"
        conteudo += "-"*60 + "\n"
        
    return conteudo.encode('utf-8')

def render_conferencia(patrimonio_db, historico_db, cidades_db=None, save_callback=None):
    st.subheader("Conferência / Auditoria de Patrimônio")

    # --- SELEÇÃO DE LOCALIZAÇÃO ---
    locais = cidades_db.get("lista", ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]) if isinstance(cidades_db, dict) else ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]
    
    local_selecionado = st.selectbox("Selecione o Local para Auditoria", locais, key="conf_local_sel")

    # Filtrar itens do local selecionado
    itens_do_local = [item for item in patrimonio_db if item.get("localizacao") == local_selecionado]
    
    # Session state para auditorias realizadas no ciclo atual
    if "auditados" not in st.session_state:
        st.session_state.auditados = {}

    total_local = len(itens_do_local)
    conferidos_local = sum(1 for item in itens_do_local if str(item.get("etiqueta")) in st.session_state.auditados)
    pendentes_local = total_local - conferidos_local

    # --- CARDS DE MÉTRICAS ---
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total no Local", total_local)
    with c2:
        st.metric("Vistoriados/Conferidos", conferidos_local)
    with c3:
        st.metric("Pendentes", pendentes_local)

    st.markdown("---")

    # --- ABAS DE VISTORIA, CHECKLIST E RELATÓRIO ---
    aba_vistoria, aba_checklist, aba_relatorio = st.tabs([
        " Vistoria e Auditoria Física", 
        " Lista de Verificação", 
        " Relatório da Vistoria"
    ])

    # -------------------------------------------------------------
    # ABA 1: VISTORIA E AUDITORIA FÍSICA
    # -------------------------------------------------------------
    with aba_vistoria:
        st.markdown("### Seleção e Registro de Vistoria")
        
        if patrimonio_db:
            opcoes_itens = ["-- Selecione o patrimônio para vistoria --"] + [
                f"{item.get('etiqueta', '')} - {item.get('nome', '')} ({item.get('localizacao', '')})"
                for item in patrimonio_db
            ]
        else:
            opcoes_itens = ["Nenhum item cadastrado"]

        item_selecionado_str = st.selectbox(
            "Pesquise ou Selecione a Etiqueta/Nome do Bem:",
            options=opcoes_itens,
            key="sb_vistoria_item"
        )

        if item_selecionado_str and item_selecionado_str not in ["-- Selecione o patrimônio para vistoria --", "Nenhum item cadastrado"]:
            etiqueta_sel = item_selecionado_str.split(" - ")[0].strip()
            idx_item = next((i for i, item in enumerate(patrimonio_db) if str(item.get("etiqueta")).strip() == etiqueta_sel), None)

            if idx_item is not None:
                item_obj = patrimonio_db[idx_item]
                
                st.info(f"**Item Selecionado:** {item_obj.get('nome')} | **Categoria:** {item_obj.get('categoria')} | **Local:** {item_obj.get('localizacao')}")

                with st.form("form_registro_vistoria", clear_on_submit=False):
                    st.markdown("####  Formulário de Auditoria Física")
                    
                    col_v1, col_v2 = st.columns(2)
                    with col_v1:
                        novo_estado = st.selectbox(
                            " Condições Físicas / Situação Atual:",
                            ["Em Uso", "Em Manutenção", "Inservível", "Baixado"],
                            index=["Em Uso", "Em Manutenção", "Inservível", "Baixado"].index(item_obj.get("estado", "Em Uso")) if item_obj.get("estado") in ["Em Uso", "Em Manutenção", "Inservível", "Baixado"] else 0
                        )
                        auditor_nome = st.text_input("Nome do Auditor/Vistoriador", value="Equipe ISPN")

                    with col_v2:
                        obs_vistoria = st.text_area(
                            "Observações da Vistoria / Avarias Identificadas:",
                            placeholder="Descreva o estado do bem, defeitos visíveis ou necessidade de reparo..."
                        )

                    st.markdown("####  Upload de Fotos da Vistoria (Até 3 Fotos)")
                    col_f1, col_f2, col_f3 = st.columns(3)
                    with col_f1:
                        foto1 = st.file_uploader("Foto 1 (Visão Geral)", type=["jpg", "jpeg", "png"], key="foto1")
                    with col_f2:
                        foto2 = st.file_uploader("Foto 2 (Etiqueta/Nº Série)", type=["jpg", "jpeg", "png"], key="foto2")
                    with col_f3:
                        foto3 = st.file_uploader("Foto 3 (Detalhe/Avaria)", type=["jpg", "jpeg", "png"], key="foto3")

                    submitted_vistoria = st.form_submit_button(" Confirmar e Salvar Vistoria", type="primary", use_container_width=True)

                    if submitted_vistoria:
                        # Processa fotos
                        fotos_anexadas = []
                        for f in [foto1, foto2, foto3]:
                            if f is not None:
                                fotos_anexadas.append({"nome": f.name, "bytes": f.getvalue()})

                        # Atualiza o estado do bem no BD geral
                        patrimonio_db[idx_item]["estado"] = novo_estado
                        
                        # Armazena dados no histórico de auditoria
                        registro_auditoria = {
                            "etiqueta": etiqueta_sel,
                            "nome": item_obj.get("nome"),
                            "categoria": item_obj.get("categoria"),
                            "localizacao": item_obj.get("localizacao"),
                            "responsavel": item_obj.get("responsavel"),
                            "estado": novo_estado,
                            "auditor": auditor_nome,
                            "obs_vistoria": obs_vistoria,
                            "qtd_fotos": len(fotos_anexadas),
                            "fotos": fotos_anexadas
                        }

                        # Atualiza o Session State da sessão atual
                        st.session_state.auditados[etiqueta_sel] = registro_auditoria

                        if save_callback:
                            save_callback()

                        st.success(f"Vistoria do item '{item_obj.get('nome')}' concluída e salva com sucesso!")
                        st.rerun()

    # -------------------------------------------------------------
    # ABA 2: LISTA DE VERIFICAÇÃO (CHECKLIST)
    # -------------------------------------------------------------
    with aba_checklist:
        st.markdown(f"### Checklist de Bens em **{local_selecionado}**")
        if itens_do_local:
            dados_checklist = []
            for item in itens_do_local:
                etiq = str(item.get("etiqueta"))
                foi_conferido = etiq in st.session_state.auditados
                audit_info = st.session_state.auditados.get(etiq, {})

                dados_checklist.append({
                    "Status": " Concluído" if foi_conferido else " Pendente",
                    "Etiqueta": etiq,
                    "Nome": item.get("nome"),
                    "Categoria": item.get("categoria"),
                    "Situação Atual": item.get("estado"),
                    "Obs. Vistoria": audit_info.get("obs_vistoria", "-"),
                    "Fotos Anexadas": audit_info.get("qtd_fotos", 0)
                })
            
            df_check = pd.DataFrame(dados_checklist)
            st.dataframe(df_check, use_container_width=True, hide_index=True)
        else:
            st.info(f"Nenhum patrimônio cadastrado para o local '{local_selecionado}'.")

    # -------------------------------------------------------------
    # ABA 3: RELATÓRIO DA VISTORIA (TODOS OU POR CATEGORIA)
    # -------------------------------------------------------------
    with aba_relatorio:
        st.markdown("### Exportar Relatório de Vistoria")
        
        if not st.session_state.auditados:
            st.warning("Nenhuma auditoria/vistoria foi realizada nesta sessão até o momento.")
        else:
            lista_auditados = list(st.session_state.auditados.values())
            
            # Filtro por Categoria para emissão do relatório
            cats_disponiveis = ["Todas"] + list(set(item["categoria"] for item in lista_auditados if item.get("categoria")))
            cat_relatorio = st.selectbox("Filtrar relatório por Categoria:", cats_disponiveis)

            if cat_relatorio != "Todas":
                itens_filtrados = [item for item in lista_auditados if item.get("categoria") == cat_relatorio]
            else:
                itens_filtrados = lista_auditados

            st.write(f"**Itens no relatório:** {len(itens_filtrados)}")
            
            # Exibe prévia dos itens no relatório
            df_rel = pd.DataFrame(itens_filtrados)[["etiqueta", "nome", "categoria", "localizacao", "estado", "obs_vistoria", "qtd_fotos"]]
            st.dataframe(df_rel, use_container_width=True, hide_index=True)

            # Botão para baixar relatório em TXT/PDF
            relatorio_bytes = gerar_relatorio_txt_pdf(itens_filtrados, cat_relatorio)
            
            st.download_button(
                label=f" Baixar Relatório de Vistoria ({cat_relatorio})",
                data=relatorio_bytes,
                file_name=f"relatorio_vistoria_{cat_relatorio.lower().replace(' ', '_')}.txt",
                mime="text/plain",
                type="primary",
                use_container_width=True
            )
