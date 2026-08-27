import streamlit as st
import pandas as pd
import os
from datetime import datetime
import importlib

DATA_DIR = "data"
ANEXOS_DIR = os.path.join(DATA_DIR, "anexos_nf")
FOTOS_DIR = os.path.join(DATA_DIR, "fotos_bens")
os.makedirs(ANEXOS_DIR, exist_ok=True)
os.makedirs(FOTOS_DIR, exist_ok=True)

# Tenta importar as funções de salvamento do banco de dados
try:
    db_mod = importlib.import_module("banco de dados.db")
except ModuleNotFoundError:
    try:
        db_mod = importlib.import_module("banco_dados.db")
    except ModuleNotFoundError:
        try:
            db_mod = importlib.import_module("database.db")
        except ModuleNotFoundError:
            db_mod = None

save_all_data = getattr(db_mod, "save_all_data", getattr(db_mod, "guardar_todos_os_dados", None)) if db_mod else None


def salvar_anexo(file_upload, subpasta="anexos_nf"):
    """Salva arquivos anexados na pasta nativa data/"""
    if file_upload is None:
        return ""
    caminho_dir = os.path.join(DATA_DIR, subpasta)
    os.makedirs(caminho_dir, exist_ok=True)
    nome_arquivo = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_upload.name}"
    caminho_completo = os.path.join(caminho_dir, nome_arquivo)
    with open(caminho_completo, "wb") as f:
        f.write(file_upload.getbuffer())
    return caminho_completo


def persistir_dados(patrimonio_db, historico_db):
    """Executa o salvamento no banco/arquivo"""
    if save_all_data:
        users_db = st.session_state.get('users_db', {})
        cidades = st.session_state.get('cidades_db', {})
        save_all_data(users_db, patrimonio_db, historico_db, cidades)
    else:
        df_salvar = pd.DataFrame(patrimonio_db)
        df_salvar.to_csv(os.path.join(DATA_DIR, "patrimonio.csv"), index=False)


def render_gestao(patrimonio_db, historico_db, cidades_db=None):
    st.title("📦 Gestão de Bens Patrimoniais")

    # Mapeamento de coluna de chave primária
    df = pd.DataFrame(patrimonio_db) if patrimonio_db else pd.DataFrame()
    col_etiqueta = 'Patrimônio' if 'Patrimônio' in df.columns else ('etiqueta' if 'etiqueta' in df.columns else 'patrimonio')

    # Lista de cidades / filiais
    lista_cidades = cidades_db.get("lista", ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]) if cidades_db else ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]

    # Mensagem mantida no session_state
    if "msg_sucesso" in st.session_state:
        st.success(st.session_state.msg_sucesso)
        del st.session_state.msg_sucesso

    aba_sub = st.tabs(["➕ Novo Item / Nota Fiscal", "📥 Importar Planilha Instituto", "✏️ Editar Item", "🗑️ Excluir Item (Admin)"])

    # --- ABA 1: NOVO ITEM ---
    with aba_sub[0]:
        st.subheader("➕ Cadastrar Novo Item")

        with st.form("form_novo_patrimonio"):
            st.markdown("### 📄 Dados da Nota Fiscal / Compra")
            c_nf1, c_nf2, c_nf3 = st.columns(3)
            with c_nf1:
                num_nf = st.text_input("Nº NF")
                data_emissao_nf = st.date_input("Data de Emissão NF", value=datetime.now())
                fornecedor = st.text_input("Fornecedor")
            with c_nf2:
                ano_compra = st.number_input("Ano", min_value=1990, max_value=2030, value=datetime.now().year)
                qtd_itens = st.number_input("Quant.", min_value=1, value=1)
                projeto = st.text_input("Projeto")
            with c_nf3:
                status_projeto = st.text_input("Status do projeto")
                anexo_nf = st.file_uploader("Upload da NOTA FISCAL (PDF/Imagem)", type=["pdf", "png", "jpg", "jpeg"])

            st.divider()
            st.markdown("### 📦 Detalhes do Patrimônio")

            c_b1, c_b2, c_b3 = st.columns(3)
            with c_b1:
                cod_patrimonio = st.text_input("Patrimônio (Código/Etiqueta) *")
                descricao_bem = st.text_input("Descrição do bem *")
                categoria_bem = st.selectbox("Categoria do bem", ["Informática", "Veículos", "Mobiliário", "Eletroeletrônicos", "Equipamento de Campo", "Outros"])
                setor = st.text_input("Setor")

            with c_b2:
                valor_bem = st.number_input("Valor do bem (R$)", min_value=0.0, format="%.2f")
                valor_laudo = st.number_input("Valor registrado no laudo (R$)", min_value=0.0, format="%.2f")
                valor_depreciado = st.number_input("Valor atualizado (depreciado) (R$)", min_value=0.0, format="%.2f")
                situacao = st.selectbox("Situação / Status", ["Em Uso", "Disponível", "Manutenção", "Baixado", "Doado"])

            with c_b3:
                localizacao = st.selectbox("Localização / Cidade", lista_cidades)
                responsavel = st.text_input("Responsável", value="Equipe ISPN")
                foto_bem = st.file_uploader("FOTO do Bem", type=["png", "jpg", "jpeg"])
                obs = st.text_area("Observações")

            btn_cadastrar = st.form_submit_button("Cadastrar Patrimônio", type="primary", use_container_width=True)

            if btn_cadastrar:
                if not cod_patrimonio or not descricao_bem:
                    st.error("Por favor, preencha os campos 'Patrimônio' e 'Descrição do bem'.")
                else:
                    caminho_nf = salvar_anexo(anexo_nf, "anexos_nf")
                    caminho_foto = salvar_anexo(foto_bem, "fotos_bens")

                    novo_reg = {
                        "Patrimônio": cod_patrimonio,
                        "etiqueta": cod_patrimonio,
                        "Ano": ano_compra,
                        "Data de Emissão NF": str(data_emissao_nf),
                        "Nº NF": num_nf,
                        "Quant.": qtd_itens,
                        "Fornecedor": fornecedor,
                        "Descrição do bem": descricao_bem,
                        "nome": descricao_bem,
                        "Categoria do bem": categoria_bem,
                        "categoria": categoria_bem,
                        "Valor do bem": valor_bem,
                        "Valor registrado no laudo": valor_laudo,
                        "Valor atualizado (depreciado)": valor_depreciado,
                        "Projeto": projeto,
                        "Status do projeto": status_projeto,
                        "Localização no escritório": localizacao,
                        "localizacao": localizacao,
                        "Responsável": responsavel,
                        "responsavel": responsavel,
                        "Setor": setor,
                        "Situação": situacao,
                        "status": situacao,
                        "TERMO DE ENTREGA": "",
                        "TERMOS DE DEVOLUÇÃO": "",
                        "TERMOS DE DOAÇÃO": "",
                        "Última conferência": "",
                        "NOTA FISCAL": caminho_nf,
                        "FOTO": caminho_foto,
                        "Observações": obs
                    }

                    patrimonio_db.append(novo_reg)

                    # Histórico
                    historico_db.append({
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "etiqueta": cod_patrimonio,
                        "item": descricao_bem,
                        "acao": "Cadastro Inicial",
                        "detalhes": f"Cadastrado em {localizacao} por {st.session_state.get('username', 'admin')}"
                    })

                    persistir_dados(patrimonio_db, historico_db)
                    st.session_state.msg_sucesso = f"Feito! O item '{descricao_bem}' ({cod_patrimonio}) foi cadastrado com sucesso."
                    st.rerun()

    # --- ABA 2: IMPORTAR PLANILHA ---
    with aba_sub[1]:
        st.subheader("📥 Importar Planilha de Patrimônio (Excel / CSV)")

        with st.expander("📋 Orientação sobre o Cabeçalho da Planilha (Modelo Instituto)", expanded=True):
            st.write("A planilha deve conter preferencialmente o cabeçalho oficial:")
            st.code("Patrimônio | Ano | Data de Emissão NF | Nº NF | Quant. | Fornecedor | Descrição do bem | Categoria do bem | Valor do bem | Valor registrado no laudo | Valor atualizado (depreciado) | Projeto | Status do projeto | Localização no escritório | Responsável | Setor | Situação | TERMO DE ENTREGA | TERMOS DE DEVOLUÇÃO | TERMOS DE DOAÇÃO | Última conferência | NOTA FISCAL | FOTO | Observações")

        arquivo = st.file_uploader("Selecione o arquivo Excel (.xlsx) ou CSV", type=["xlsx", "xls", "csv"], key="import_file")

        if arquivo:
            try:
                if arquivo.name.endswith(".csv"):
                    df_importado = pd.read_csv(arquivo)
                else:
                    df_importado = pd.read_excel(arquivo)

                st.markdown("**Pré-visualização da planilha:**")
                st.dataframe(df_importado.head(5), use_container_width=True)

                if st.button("Confirmar Importação de Dados", type="primary"):
                    novos_registros = df_importado.to_dict(orient="records")
                    
                    # Garante compatibilidade de chaves para leituras antigas
                    for r in novos_registros:
                        r['etiqueta'] = r.get('Patrimônio', r.get('etiqueta', ''))
                        r['nome'] = r.get('Descrição do bem', r.get('nome', ''))
                        r['categoria'] = r.get('Categoria do bem', r.get('categoria', ''))
                        r['localizacao'] = r.get('Localização no escritório', r.get('localizacao', ''))
                        r['status'] = r.get('Situação', r.get('status', ''))
                        r['responsavel'] = r.get('Responsável', r.get('responsavel', ''))

                    patrimonio_db.extend(novos_registros)

                    historico_db.append({
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "etiqueta": "LOTE",
                        "item": f"{len(novos_registros)} itens",
                        "acao": "Importação em Lote",
                        "detalhes": f"Importado por {st.session_state.get('username', 'admin')}"
                    })

                    persistir_dados(patrimonio_db, historico_db)
                    st.session_state.msg_sucesso = f"Sucesso! {len(novos_registros)} bens patrimoniais foram importados."
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {e}")

    # --- ABA 3: EDITAR ITEM ---
    with aba_sub[2]:
        st.subheader("✏️ Editar ou Transferir Item")
        if patrimonio_db:
            opcoes_itens = [f"{item.get('Patrimônio', item.get('etiqueta', ''))} - {item.get('Descrição do bem', item.get('nome', ''))}" for item in patrimonio_db]
            item_sel = st.selectbox("Selecione o Item para Editar:", opcoes_itens, key="edit_sel")

            codigo_sel = item_sel.split(" - ")[0]
            idx = next((i for i, item in enumerate(patrimonio_db) if str(item.get('Patrimônio', item.get('etiqueta', ''))) == codigo_sel), None)

            if idx is not None:
                item_dados = patrimonio_db[idx]

                c_edit1, c_edit2 = st.columns(2)
                with c_edit1:
                    e_nome = st.text_input("Descrição do Bem", value=item_dados.get('Descrição do bem', item_dados.get('nome', '')), key="e_nome")
                    
                    cat_atual = item_dados.get('Categoria do bem', item_dados.get('categoria', 'Outros'))
                    cats_lista = ["Informática", "Veículos", "Mobiliário", "Eletroeletrônicos", "Equipamento de Campo", "Outros"]
                    cat_idx = cats_lista.index(cat_atual) if cat_atual in cats_lista else 0
                    e_cat = st.selectbox("Categoria", cats_lista, index=cat_idx, key="e_cat")

                    e_setor = st.text_input("Setor", value=item_dados.get('Setor', ''), key="e_setor")
                    e_val = st.number_input("Valor do Bem (R$)", value=float(item_dados.get('Valor do bem', 0.0) or 0.0), key="e_val")

                with c_edit2:
                    loc_atual = item_dados.get('Localização no escritório', item_dados.get('localizacao', lista_cidades[0]))
                    loc_idx = lista_cidades.index(loc_atual) if loc_atual in lista_cidades else 0
                    e_local = st.selectbox("Cidade / Localização", lista_cidades, index=loc_idx, key="e_loc")

                    stat_atual = item_dados.get('Situação', item_dados.get('status', 'Em Uso'))
                    stats_lista = ["Em Uso", "Disponível", "Manutenção", "Baixado", "Doado"]
                    stat_idx = stats_lista.index(stat_atual) if stat_atual in stats_lista else 0
                    e_stat = st.selectbox("Situação", stats_lista, index=stat_idx, key="e_stat")

                    e_resp = st.text_input("Responsável", value=item_dados.get('Responsável', item_dados.get('responsavel', '')), key="e_resp")

                if st.button("Salvar Alterações", type="primary", use_container_width=True):
                    patrimonio_db[idx]['Descrição do bem'] = e_nome
                    patrimonio_db[idx]['nome'] = e_nome
                    patrimonio_db[idx]['Categoria do bem'] = e_cat
                    patrimonio_db[idx]['categoria'] = e_cat
                    patrimonio_db[idx]['Setor'] = e_setor
                    patrimonio_db[idx]['Valor do bem'] = e_val
                    patrimonio_db[idx]['Localização no escritório'] = e_local
                    patrimonio_db[idx]['localizacao'] = e_local
                    patrimonio_db[idx]['Situação'] = e_stat
                    patrimonio_db[idx]['status'] = e_stat
                    patrimonio_db[idx]['Responsável'] = e_resp
                    patrimonio_db[idx]['responsavel'] = e_resp

                    historico_db.append({
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "etiqueta": codigo_sel,
                        "item": e_nome,
                        "acao": "Atualização",
                        "detalhes": f"Editado por {st.session_state.get('username', 'admin')}"
                    })

                    persistir_dados(patrimonio_db, historico_db)
                    st.session_state.msg_sucesso = "Dados do item atualizados com sucesso!"
                    st.rerun()

    # --- ABA 4: EXCLUIR ITEM ---
    with aba_sub[3]:
        st.subheader("🗑️ Excluir Item")
        if st.session_state.get("role") != "admin":
            st.warning("Apenas usuários Administradores podem excluir itens.")
        elif patrimonio_db:
            opcoes_itens_del = [f"{item.get('Patrimônio', item.get('etiqueta', ''))} - {item.get('Descrição do bem', item.get('nome', ''))}" for item in patrimonio_db]
            item_del_sel = st.selectbox("Selecione o Item para Excluir:", opcoes_itens_del, key="del_sel")

            if st.button("Excluir Definitivamente", type="primary", use_container_width=True):
                codigo_del = item_del_sel.split(" - ")[0]
                patrimonio_db[:] = [i for i in patrimonio_db if str(i.get('Patrimônio', i.get('etiqueta', ''))) != codigo_del]

                historico_db.append({
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "etiqueta": codigo_del,
                    "item": item_del_sel,
                    "acao": "Exclusão",
                    "detalhes": f"Excluído por {st.session_state.get('username', 'admin')}"
                })

                persistir_dados(patrimonio_db, historico_db)
                st.session_state.msg_sucesso = f"Item {codigo_del} excluído com sucesso!"
                st.rerun()

    st.divider()

    # --- TABELA DE VISUALIZAÇÃO GERAL ---
    st.subheader("📋 Relação de Bens Patrimoniais")
    if patrimonio_db:
        st.dataframe(pd.DataFrame(patrimonio_db), use_container_width=True)
    else:
        st.info("Nenhum patrimônio cadastrado até o momento.")
