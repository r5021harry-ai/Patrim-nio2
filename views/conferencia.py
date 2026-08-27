import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

def normalizar_texto(texto):
    """
    Remove caracteres incompatíveis com a codificação Latin-1 padrão do FPDF.
    """
    if texto is None:
        return ""
    txt = str(texto)
    substituicoes = {
        "–": "-", "—": "-", "“": '"', "”": '"', "‘": "'", "’": "'",
        "º": ".", "ª": ".", "•": "-"
    }
    for orig, dest in substituicoes.items():
        txt = txt.replace(orig, dest)
    
    return txt.encode('latin-1', 'replace').decode('latin-1')

class PDFRelatorioVistoria(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, normalizar_texto('RELATÓRIO DE AUDITORIA E VISTORIA DE PATRIMÔNIO'), 0, 1, 'C')
        self.set_font('Arial', 'I', 9)
        dt_str = datetime.now().strftime("%d/%m/%Y as %H:%M:%S")
        self.cell(0, 5, normalizar_texto(f'Gerado em: {dt_str}'), 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, normalizar_texto(f'Página {self.page_no()}'), 0, 0, 'C')

def gerar_pdf_vistoria(itens_auditados, filtro_categoria="Todas"):
    pdf = PDFRelatorioVistoria()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, normalizar_texto(f"Filtro por Categoria: {filtro_categoria}"), 0, 1, 'L')
    pdf.cell(0, 8, normalizar_texto(f"Total de Itens Auditados: {len(itens_auditados)}"), 0, 1, 'L')
    pdf.ln(3)

    for idx, item in enumerate(itens_auditados, 1):
        pdf.set_fill_color(230, 240, 230)
        pdf.set_font("Arial", "B", 10)
        
        nome_bem = normalizar_texto(item.get('nome', 'N/A'))
        pdf.cell(0, 7, normalizar_texto(f"Item #{idx} - {nome_bem}"), 1, 1, 'L', fill=True)
        
        pdf.set_font("Arial", size=9)
        
        val_float = item.get("valor_unitario", 0.0)
        val_str = f"R$ {val_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        etiq = normalizar_texto(item.get('etiqueta', 'N/A'))
        cat = normalizar_texto(item.get('categoria', 'N/A'))
        loc = normalizar_texto(item.get('localizacao', 'N/A'))
        resp = normalizar_texto(item.get('responsavel', 'N/A'))
        est = normalizar_texto(item.get('estado', 'N/A'))
        aud = normalizar_texto(item.get('auditor', 'N/A'))
        dt_vist = normalizar_texto(item.get('data_vistoria', 'N/A'))
        obs = normalizar_texto(item.get('obs_vistoria', 'Sem observações'))

        bloco_texto = (
            f"- Etiqueta/Codigo: {etiq} | Categoria: {cat}\n"
            f"- Localizacao: {loc} | Responsavel: {resp}\n"
            f"- Valor do Bem: {val_str} | Data da Vistoria: {dt_vist}\n"
            f"- Condicao/Situacao Atual: {est} | Auditor Responsavel: {aud}\n"
            f"- Fotos Anexadas: {item.get('qtd_fotos', 0)} foto(s)\n"
            f"- Observacoes/Avarias: {obs}"
        )

        pdf.multi_cell(0, 5, normalizar_texto(bloco_texto), border=1)
        pdf.ln(4)

    return bytes(pdf.output(dest='S'))

def render_conferencia(patrimonio_db, historico_db, cidades_db=None, save_callback=None):
    st.subheader("Conferência / Auditoria de Patrimônio")

    locais = cidades_db.get("lista", ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]) if isinstance(cidades_db, dict) else ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]
    local_selecionado = st.selectbox("Selecione o Local para Auditoria", locais, key="conf_local_sel")

    itens_do_local = [item for item in patrimonio_db if item.get("localizacao") == local_selecionado]
    
    if "auditados" not in st.session_state:
        st.session_state.auditados = {}

    total_local = len(itens_do_local)
    conferidos_local = sum(1 for item in itens_do_local if str(item.get("etiqueta")) in st.session_state.auditados)
    pendentes_local = total_local - conferidos_local

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total no Local", total_local)
    with c2:
        st.metric("Vistoriados/Conferidos", conferidos_local)
    with c3:
        st.metric("Pendentes", pendentes_local)

    st.markdown("---")

    aba_vistoria, aba_checklist, aba_relatorio = st.tabs([
        "Vistoria e Auditoria Física", 
        "Lista de Verificação", 
        "Relatório da Vistoria (PDF)"
    ])

    # -------------------------------------------------------------
    # ABA 1: VISTORIA E AUDITORIA FÍSICA
    # -------------------------------------------------------------
    with aba_vistoria:
        st.markdown("### Seleção e Registro de Vistoria")
        
        # Exibe mensagem de sucesso se a última vistoria foi salva com êxito
        if st.session_state.get("sucesso_vistoria_msg"):
            st.success(st.session_state.sucesso_vistoria_msg)
            del st.session_state["sucesso_vistoria_msg"]

        if patrimonio_db:
            opcoes_itens = ["-- Selecione o patrimônio para vistoria --"] + [
                f"{item.get('etiqueta', '')} - {item.get('nome', '')} ({item.get('localizacao', '')})"
                for item in patrimonio_db
            ]
        else:
            opcoes_itens = ["Nenhum item cadastrado"]

        # Controle da seleção no session_state para permitir reset
        if "sb_vistoria_item_val" not in st.session_state:
            st.session_state.sb_vistoria_item_val = opcoes_itens[0]

        item_selecionado_str = st.selectbox(
            "Pesquise ou Selecione a Etiqueta/Nome do Bem:",
            options=opcoes_itens,
            key="sb_vistoria_item_val"
        )

        if item_selecionado_str and item_selecionado_str not in ["-- Selecione o patrimônio para vistoria --", "Nenhum item cadastrado"]:
            etiqueta_sel = item_selecionado_str.split(" - ")[0].strip()
            idx_item = next((i for i, item in enumerate(patrimonio_db) if str(item.get("etiqueta")).strip() == etiqueta_sel), None)

            if idx_item is not None:
                item_obj = patrimonio_db[idx_item]
                val_float = item_obj.get("valor_unitario", item_obj.get("valor", 0.0))
                val_str = f"R$ {val_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                
                st.info(f"**Item:** {item_obj.get('nome')} | **Categoria:** {item_obj.get('categoria')} | **Valor:** {val_str} | **Local:** {item_obj.get('localizacao')}")

                # Form com limpa automática (clear_on_submit=True)
                with st.form("form_registro_vistoria", clear_on_submit=True):
                    st.markdown("#### Formulário de Auditoria Física")
                    
                    col_v1, col_v2 = st.columns(2)
                    with col_v1:
                        novo_estado = st.selectbox(
                            "Condições Físicas / Situação Atual:",
                            ["Em Uso", "Em Manutenção", "Inservível", "Baixado"],
                            index=["Em Uso", "Em Manutenção", "Inservível", "Baixado"].index(item_obj.get("estado", "Em Uso")) if item_obj.get("estado") in ["Em Uso", "Em Manutenção", "Inservível", "Baixado"] else 0
                        )
                        auditor_nome = st.text_input("Nome do Auditor/Vistoriador", value="Equipe ISPN")

                    with col_v2:
                        obs_vistoria = st.text_area(
                            "Observações da Vistoria / Avarias Identificadas:",
                            placeholder="Descreva o estado do bem, defeitos visíveis ou necessidade de reparo..."
                        )

                    # Campo Único para até 3 Fotos
                    fotos_anexadas_upload = st.file_uploader(
                        "Upload de Fotos da Vistoria (Selecione até 3 fotos)", 
                        type=["jpg", "jpeg", "png"], 
                        accept_multiple_files=True,
                        key="fotos_vistoria_unicas"
                    )

                    submitted_vistoria = st.form_submit_button("Confirmar e Salvar Vistoria", type="primary", use_container_width=True)

                    if submitted_vistoria:
                        fotos_anexadas = []
                        if fotos_anexadas_upload:
                            for f in fotos_anexadas_upload[:3]:
                                fotos_anexadas.append({"nome": f.name, "bytes": f.getvalue()})

                        # Atualiza estado no BD geral
                        patrimonio_db[idx_item]["estado"] = novo_estado
                        dt_atual = datetime.now().strftime("%d/%m/%Y %H:%M")

                        # Salva item vistoriado
                        registro_auditoria = {
                            "etiqueta": etiqueta_sel,
                            "nome": item_obj.get("nome"),
                            "categoria": item_obj.get("categoria"),
                            "localizacao": item_obj.get("localizacao"),
                            "responsavel": item_obj.get("responsavel"),
                            "valor_unitario": val_float,
                            "estado": novo_estado,
                            "auditor": auditor_nome,
                            "data_vistoria": dt_atual,
                            "obs_vistoria": obs_vistoria if obs_vistoria else "Sem observações",
                            "qtd_fotos": len(fotos_anexadas),
                            "fotos": fotos_anexadas
                        }

                        st.session_state.auditados[etiqueta_sel] = registro_auditoria

                        if save_callback:
                            save_callback()

                        # Define mensagem e reseta o selectbox para o próximo item
                        st.session_state.sucesso_vistoria_msg = f"OK! Vistoria do item '{item_obj.get('nome')}' gravada com sucesso!"
                        st.session_state.sb_vistoria_item_val = opcoes_itens[0]
                        st.toast("Vistoria salva com sucesso!", icon="✅")
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

                val_f = item.get("valor_unitario", item.get("valor", 0.0))
                val_s = f"R$ {val_f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                dados_checklist.append({
                    "Status": "Concluído" if foi_conferido else "Pendente",
                    "Etiqueta": etiq,
                    "Nome": item.get("nome"),
                    "Valor": val_s,
                    "Data Vistoria": audit_info.get("data_vistoria", "-"),
                    "Situação Atual": item.get("estado"),
                    "Obs. Vistoria": audit_info.get("obs_vistoria", "-"),
                    "Fotos": audit_info.get("qtd_fotos", 0)
                })
            
            df_check = pd.DataFrame(dados_checklist)
            st.dataframe(df_check, use_container_width=True, hide_index=True)
        else:
            st.info(f"Nenhum patrimônio cadastrado para o local '{local_selecionado}'.")

    # -------------------------------------------------------------
    # ABA 3: RELATÓRIO DA VISTORIA EM PDF
    # -------------------------------------------------------------
    with aba_relatorio:
        st.markdown("### Exportar Relatório de Vistoria em PDF")
        
        if not st.session_state.auditados:
            st.warning("Nenhuma auditoria/vistoria foi realizada nesta sessão até o momento.")
        else:
            lista_auditados = list(st.session_state.auditados.values())
            
            cats_disponiveis = ["Todas"] + list(set(item["categoria"] for item in lista_auditados if item.get("categoria")))
            cat_relatorio = st.selectbox("Filtrar relatório por Categoria:", cats_disponiveis)

            if cat_relatorio != "Todas":
                itens_filtrados = [item for item in lista_auditados if item.get("categoria") == cat_relatorio]
            else:
                itens_filtrados = lista_auditados

            st.write(f"**Itens no relatório:** {len(itens_filtrados)}")
            
            dados_prev = []
            for it in itens_filtrados:
                vf = it.get("valor_unitario", 0.0)
                dados_prev.append({
                    "Etiqueta": it.get("etiqueta"),
                    "Nome": it.get("nome"),
                    "Valor": f"R$ {vf:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    "Data Vistoria": it.get("data_vistoria"),
                    "Condição": it.get("estado"),
                    "Auditor": it.get("auditor"),
                    "Observações": it.get("obs_vistoria"),
                    "Fotos": it.get("qtd_fotos")
                })
            
            st.dataframe(pd.DataFrame(dados_prev), use_container_width=True, hide_index=True)

            pdf_bytes = gerar_pdf_vistoria(itens_filtrados, cat_relatorio)
            
            st.download_button(
                label=f"Baixar Relatório em PDF ({cat_relatorio})",
                data=pdf_bytes,
                file_name=f"relatorio_vistoria_{cat_relatorio.lower().replace(' ', '_')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
