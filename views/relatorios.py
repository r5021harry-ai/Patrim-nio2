import streamlit as st
import pandas as pd
import io
import base64

def render_relatorios(patrimonio_db, historico_db, cidades_db=None):
    st.title("📑 Relatórios & Auditorias")

    if not patrimonio_db:
        st.warning("Não há dados patrimoniais cadastrados para gerar relatórios.")
        return

    df = pd.DataFrame(patrimonio_db)

    # Mapeamento dinâmico das colunas
    col_etiqueta = 'patrimonio' if 'patrimonio' in df.columns else ('etiqueta' if 'etiqueta' in df.columns else df.columns[0])
    col_nome = 'descricao' if 'descricao' in df.columns else ('nome' if 'nome' in df.columns else ('item' if 'item' in df.columns else df.columns[1]))
    col_categoria = 'tipo' if 'tipo' in df.columns else ('categoria' if 'categoria' in df.columns else df.columns[2])
    col_local = 'cidade' if 'cidade' in df.columns else ('localizacao' if 'localizacao' in df.columns else df.columns[3])
    col_status = 'estado' if 'estado' in df.columns else ('status' if 'status' in df.columns else df.columns[4])

    aba_rel = st.tabs([
        "📸 Histórico de Vistorias & Fotos", 
        "🔍 Relação Geral & Filtros", 
        "📜 Histórico Geral do Sistema"
    ])

    # --- ABA 1: HISTÓRICO EXCLUSIVO DE VISTORIAS E FOTOS ---
    with aba_rel[0]:
        st.subheader("📸 Painel Exclusivo de Vistorias Realizadas")
        st.caption("Consulte aqui somente as auditorias registradas com seus respectivos estados e fotos de comprovação.")

        # Filtra apenas registros de vistoria
        vistorias = [h for h in (historico_db or []) if h.get('acao') in ["Auditoria / Vistoria", "Auditoria", "Vistoria"]]

        if not vistorias:
            st.info("Nenhuma vistoria ou auditoria foi realizada até o momento.")
        else:
            st.markdown(f"**Total de vistorias realizadas:** `{len(vistorias)}`")
            st.divider()

            # Filtro rápido por código de patrimônio dentro das vistorias
            codigos_vistoriados = sorted(list(set([v.get('etiqueta', '') for v in vistorias if v.get('etiqueta')])))
            filtro_cod = st.selectbox("Filtrar por Código de Patrimônio:", ["-- Exibir Todos --"] + codigos_vistoriados)

            vistorias_exibir = vistorias
            if filtro_cod != "-- Exibir Todos --":
                vistorias_exibir = [v for v in vistorias if v.get('etiqueta') == filtro_cod]

            # Exibição dos cards de vistoria
            for vistoria in reversed(vistorias_exibir):
                data_v = vistoria.get('data', 'Data N/I')
                etiq_v = vistoria.get('etiqueta', 'N/I')
                item_v = vistoria.get('item', 'Item sem nome')
                detalhes_v = vistoria.get('detalhes', '')
                foto_b64 = vistoria.get('foto', '')

                with st.container():
                    st.markdown(f"#### 📦 {item_v} — Código: `{etiq_v}`")
                    st.caption(f"🗓️ **Data/Hora:** {data_v}")

                    col_card_info, col_card_img = st.columns([2, 1])

                    with col_card_info:
                        # Formata os detalhes para exibição limpa
                        if "|" in detalhes_v:
                            partes = detalhes_v.split("|")
                            for parte in partes:
                                st.write(f"• {parte.strip()}")
                        else:
                            st.write(detalhes_v)

                    with col_card_img:
                        if foto_b64:
                            try:
                                img_bytes = base64.b64decode(foto_b64)
                                st.image(img_bytes, caption=f"Foto da Vistoria ({etiq_v})", use_container_width=True)
                            except Exception:
                                st.warning("Erro ao carregar a imagem desta vistoria.")
                        else:
                            st.info("📷 Vistoria realizada sem anexar foto.")

                    st.divider()

    # --- ABA 2: FILTROS E EXPORTAÇÃO ---
    with aba_rel[1]:
        st.subheader("🔍 Filtrar e Exportar Patrimônio")

        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            cats = df[col_categoria].unique().tolist() if col_categoria in df.columns else []
            cat_filtro = st.multiselect("Categoria", options=cats, default=cats)

        with col_f2:
            stats = df[col_status].unique().tolist() if col_status in df.columns else []
            stat_filtro = st.multiselect("Status", options=stats, default=stats)

        with col_f3:
            locs = df[col_local].unique().tolist() if col_local in df.columns else []
            loc_filtro = st.multiselect("Localização / Cidade", options=locs, default=locs)

        df_filtrado = df.copy()

        if col_categoria in df_filtrado.columns and cat_filtro:
            df_filtrado = df_filtrado[df_filtrado[col_categoria].isin(cat_filtro)]

        if col_status in df_filtrado.columns and stat_filtro:
            df_filtrado = df_filtrado[df_filtrado[col_status].isin(stat_filtro)]

        if col_local in df_filtrado.columns and loc_filtro:
            df_filtrado = df_filtrado[df_filtrado[col_local].isin(loc_filtro)]

        st.markdown(f"**Itens Encontrados:** `{len(df_filtrado)}` de `{len(df)}`")
        st.dataframe(df_filtrado, use_container_width=True)

        st.markdown("---")
        c_exp1, c_exp2 = st.columns(2)

        with c_exp1:
            csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar Relatório em CSV",
                data=csv_data,
                file_name="relatorio_patrimonio_ispn.csv",
                mime="text/csv",
                use_container_width=True
            )

        with c_exp2:
            buffer_excel = io.BytesIO()
            with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
                df_filtrado.to_excel(writer, index=False, sheet_name="Patrimonio")
            excel_bytes = buffer_excel.getvalue()

            st.download_button(
                label="📊 Baixar Relatório em Excel (.xlsx)",
                data=excel_bytes,
                file_name="relatorio_patrimonio_ispn.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )

    # --- ABA 3: HISTÓRICO GERAL ---
    with aba_rel[2]:
        st.subheader("📜 Histórico Geral de Modificações do Sistema")
        if historico_db:
            df_hist = pd.DataFrame(historico_db)
            # Remove a coluna de foto base64 pesada da visualização em tabela simples
            if 'foto' in df_hist.columns:
                df_hist = df_hist.drop(columns=['foto'])
            st.dataframe(df_hist, use_container_width=True)
        else:
            st.info("Nenhum histórico registrado no sistema até o momento.")
