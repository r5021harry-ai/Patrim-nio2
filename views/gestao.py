import streamlit as st
import pandas as pd
from datetime import datetime
import importlib

# Tenta importar as funções de salvamento do banco de dados
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

    # Mapeamento dinâmico de colunas
    df = pd.DataFrame(patrimonio_db) if patrimonio_db else pd.DataFrame()
    
    col_etiqueta = 'etiqueta' if 'etiqueta' in df.columns else 'patrimonio'
    col_nome = 'item' if 'item' in df.columns else ('nome' if 'nome' in df.columns else 'descricao')
    col_categoria = 'categoria' if 'categoria' in df.columns else 'tipo'
    col_local = 'localizacao' if 'localizacao' in df.columns else 'cidade'
    col_status = 'status' if 'status' in df.columns else 'estado'
    col_responsavel = 'responsavel' if 'responsavel' in df.columns else 'usuario'

    # Lista de cidades
    lista_cidades = cidades_db.get("lista", ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]) if cidades_db else ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]

    aba_sub = st.tabs(["➕ Novo Item", "✏️ Editar Item", "🗑️ Excluir Item (Admin)"])

    # --- ABA 1: NOVO ITEM ---
    with aba_sub[0]:
        st.subheader("➕ Cadastrar Novo Item")
        
        # Gerar próximo código PAT
        proximo_num = len(patrimonio_db) + 1
        codigo_sugerido = f"PAT-{proximo_num:03d}"

        # Usamos formulário, mas o campo de categoria fica fora do formulário para o Streamlit reagir ao vivo
        col_a, col_b = st.columns(2)
        with col_a:
            etiqueta = st.text_input("Código / Etiqueta", value=codigo_sugerido, key="cad_etiq")
            nome_bem = st.text_input("Nome do Bem", key="cad_nome")
            categoria = st.selectbox(
                "Categoria", 
                ["Veículo", "Informática", "Mobiliário", "Eletrodoméstico", "Equipamento de Campo", "Outros"],
                key="cad_cat"
            )
            
            # CAMPO DINÂMICO DE PLACA
            placa = ""
            if categoria == "Veículo":
                placa = st.text_input("Placa do Veículo (ex: ABC-1234 ou ABC1D23)", key="cad_placa").strip().upper()

        with col_b:
            cidade = st.selectbox("Cidade / Filial", lista_cidades, key="cad_cid")
            status = st.selectbox("Status Inicial", ["Disponível", "Em Uso", "Manutenção"], key="cad_stat")
            responsavel = st.text_input("Responsável Inicial", value="Equipe ISPN", key="cad_resp")

        if st.button("Cadastrar Patrimônio", type="primary", use_container_width=True):
            if not nome_bem:
                st.error("Por favor, preencha o Nome do Bem.")
            elif categoria == "Veículo" and not placa:
                st.warning("Por favor, insira a Placa do Veículo.")
            else:
                # Se for veículo, concatena a placa ou salva no objeto
                nome_final = f"{nome_bem} (Placa: {placa})" if (categoria == "Veículo" and placa) else nome_bem

                novo_reg = {
                    col_etiqueta: etiqueta,
                    col_nome: nome_final,
                    col_categoria: categoria,
                    col_local: cidade,
                    col_status: status,
                    col_responsavel: responsavel,
                    "placa": placa if categoria == "Veículo" else ""
                }
                
                patrimonio_db.append(novo_reg)
                
                # Registra no histórico
                historico_db.append({
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "etiqueta": etiqueta,
                    "item": nome_final,
                    "acao": "Cadastro Inicial",
                    "detalhes": f"Cadastrado em {cidade} por {st.session_state.get('username', 'admin')}"
                })

                # Salva os dados
                if save_all_data:
                    users_db = st.session_state.get('users_db', {})
                    cidades = st.session_state.get('cidades_db', {})
                    save_all_data(users_db, patrimonio_db, historico_db, cidades)

                st.success(f"Feito! O item '{nome_final}' ({etiqueta}) foi cadastrado com sucesso.")
                st.rerun()

    # --- ABA 2: EDITAR ITEM ---
    with aba_sub[1]:
        st.subheader("✏️ Editar ou Transferir Item")
        if patrimonio_db:
            opcoes_itens = [f"{item.get(col_etiqueta, '')} - {item.get(col_nome, '')}" for item in patrimonio_db]
            item_sel = st.selectbox("Selecione o Item para Editar:", opcoes_itens, key="edit_sel")
            
            codigo_sel = item_sel.split(" - ")[0]
            idx = next((i for i, item in enumerate(patrimonio_db) if str(item.get(col_etiqueta)) == codigo_sel), None)

            if idx is not None:
                item_dados = patrimonio_db[idx]
                
                c_edit1, c_edit2 = st.columns(2)
                with c_edit1:
                    e_nome = st.text_input("Nome do Bem", value=item_dados.get(col_nome, ""), key="e_nome")
                    
                    cat_atual = item_dados.get(col_categoria, "Outros")
                    cats_lista = ["Veículo", "Informática", "Mobiliário", "Eletrodoméstico", "Equipamento de Campo", "Outros"]
                    cat_idx = cats_lista.index(cat_atual) if cat_atual in cats_lista else 0
                    
                    e_cat = st.selectbox("Categoria", cats_lista, index=cat_idx, key="e_cat")

                    e_placa = ""
                    if e_cat == "Veículo":
                        placa_atual = item_dados.get("placa", "")
                        e_placa = st.text_input("Placa do Veículo", value=placa_atual, key="e_placa").strip().upper()

                with c_edit2:
                    loc_atual = item_dados.get(col_local, lista_cidades[0])
                    loc_idx = lista_cidades.index(loc_atual) if loc_atual in lista_cidades else 0
                    e_local = st.selectbox("Cidade / Localização", lista_cidades, index=loc_idx, key="e_loc")

                    stat_atual = item_dados.get(col_status, "Disponível")
                    stats_lista = ["Disponível", "Em Uso", "Manutenção"]
                    stat_idx = stats_lista.index(stat_atual) if stat_atual in stats_lista else 0
                    e_stat = st.selectbox("Status", stats_lista, index=stat_idx, key="e_stat")

                    e_resp = st.text_input("Responsável", value=item_dados.get(col_responsavel, ""), key="e_resp")

                if st.button("Salvar Alterações", type="primary", use_container_width=True):
                    patrimonio_db[idx][col_nome] = e_nome
                    patrimonio_db[idx][col_categoria] = e_cat
                    patrimonio_db[idx][col_local] = e_local
                    patrimonio_db[idx][col_status] = e_stat
                    patrimonio_db[idx][col_responsavel] = e_resp
                    if e_cat == "Veículo":
                        patrimonio_db[idx]["placa"] = e_placa

                    # Registro de histórico
                    historico_db.append({
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "etiqueta": codigo_sel,
                        "item": e_nome,
                        "acao": "Atualização",
                        "detalhes": f"Editado por {st.session_state.get('username', 'admin')}"
                    })

                    if save_all_data:
                        users_db = st.session_state.get('users_db', {})
                        cidades = st.session_state.get('cidades_db', {})
                        save_all_data(users_db, patrimonio_db, historico_db, cidades)

                    st.success("Dados atualizados com sucesso!")
                    st.rerun()

    # --- ABA 3: EXCLUIR ITEM ---
    with aba_sub[2]:
        st.subheader("🗑️ Excluir Item")
        if st.session_state.get("role") != "admin":
            st.warning("Apenas usuários Administradores podem excluir itens.")
        elif patrimonio_db:
            opcoes_itens_del = [f"{item.get(col_etiqueta, '')} - {item.get(col_nome, '')}" for item in patrimonio_db]
            item_del_sel = st.selectbox("Selecione o Item para Excluir:", opcoes_itens_del, key="del_sel")
            
            if st.button("Excluir Definitivamente", type="primary", use_container_width=True):
                codigo_del = item_del_sel.split(" - ")[0]
                patrimonio_db[:] = [i for i in patrimonio_db if str(i.get(col_etiqueta)) != codigo_del]
                
                if save_all_data:
                    users_db = st.session_state.get('users_db', {})
                    cidades = st.session_state.get('cidades_db', {})
                    save_all_data(users_db, patrimonio_db, historico_db, cidades)

                st.success(f"Item {codigo_del} excluído!")
                st.rerun()

    st.divider()

    # --- TABELA DE VISUALIZAÇÃO GERAL ---
    st.subheader("📋 Relação de Bens Patrimoniais")
    if patrimonio_db:
        st.dataframe(pd.DataFrame(patrimonio_db), use_container_width=True)
