import streamlit as st
import pandas as pd
import io
import base64
import importlib

# Tenta importar salvamento do banco de dados
try:
    db_mod = importlib.import_module("banco de dados.db")
except ModuleNotFoundError:
    try:
        db_mod = importlib.import_module("banco_dados.db")
    except ModuleNotFoundError:
        db_mod = importlib.import_module("database.db")

save_all_data = getattr(db_mod, "save_all_data", getattr(db_mod, "guardar_todos_os_dados", None))

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

    # --- ABA 1: HISTÓRICO DE VISTORIAS E FOTOS ---
    with aba_rel[0]:
        st.subheader("📸 Painel Exclusivo de Vistorias Realizadas")
        st.caption("Consulte as auditorias registradas e faça a gestão das fotos e registros.")

        # Filtra apenas registros de vistoria
        vistorias = [h for h in (historico_db or []) if h.get('acao') in ["Auditoria / Vistoria", "Auditoria", "Vistoria"]]

        if not vistorias:
            st.info("Nenhuma vistoria ou auditoria foi realizada até o momento.")
        else:
            # --- PAINEL EXCLUSIVO DE ADMIN (EXCLUSÃO DE FOTOS / VISTORIAS) ---
            if st.session_state.get("role") == "admin":
                with st.expander("⚙️ Gerenciar / Excluir Vistorias e Fotos (Apenas Admin)", expanded=False):
                    st.warning("⚠️ Atenção: Ações realizadas aqui afetam permanentemente o histórico do banco de dados.")
                    
                    opcoes_vistoria = [
                        f"{v.get('data', 'Data N/I')} - {v.get('etiqueta', '')} ({v.get('item', 'Item')})" 
                        for v in vistorias
                    ]
                    
                    vistoria_sel = st.selectbox("Selecione a Vistoria:", opcoes_vistoria, key="sel_vistoria_adm")
                    
                    if vistoria_sel:
                        idx_hist = next((i for i, h in enumerate(historico_db) if f"{h.get('data', 'Data N/I')} - {h.get('etiqueta', '')} ({h.get('item', 'Item')})" == vistoria_sel), None)
                        
                        if idx_hist is not None:
                            c_adm1, c_adm2 = st.columns(2)
                            
                            with c_adm1:
                                if st.button("🗑️ Apagar Apenas a Foto desta Vistoria", use_container_width=True):
                                    historico_db[idx_hist]['foto'] = ""
                                    if save_all_data:
                                        users_db = st.session_state.get('users_db', {})
                                        cidades = st.session_state.get('cidades_db', {})
                                        save_all_data(users_db, patrimonio_db, historico_db, cidades)
                                    st.success("Foto removida com sucesso para liberar espaço!")
                                    st.rerun()

                            with c_adm2:
                                if st.button("🚨 Excluir Vistoria Completa", type="primary", use_container_width=True):
                                    historico_db.pop(idx_hist)
                                    if save_all_data:
                                        users_db = st.session_state.get('users_db', {})
                                        cidades = st.session_state.get('cidades_db', {})
                                        save_all_data(users_db, patrimonio_db, historico_db, cidades)
                                    st.success("Registro de vistoria excluído com sucesso!")
                                    st.rerun()

            st.divider()

            # Filtro rápido por código de patrimônio
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
                            st.info("📷 Nenhuma foto anexada nesta vistoria.")

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
            if 'foto' in df_hist.columns:
                df_hist = df_hist.drop(columns=['foto'])
            st.dataframe(df_hist, use_container_width=True)
        else:
            st.info("Nenhum histórico registrado no sistema até o momento.")
