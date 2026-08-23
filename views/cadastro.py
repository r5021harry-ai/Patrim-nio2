import streamlit as st
from datetime import datetime
import importlib

# Importa salvamento
try:
    db_mod = importlib.import_module("banco de dados.db")
except ModuleNotFoundError:
    try:
        db_mod = importlib.import_module("banco_dados.db")
    except ModuleNotFoundError:
        db_mod = importlib.import_module("database.db")

save_all_data = getattr(db_mod, "save_all_data", getattr(db_mod, "guardar_todos_os_dados", None))

def excluir_patrimonio(idx_item):
    """Função auxiliar para remover e salvar permanentemente."""
    item_removido = st.session_state.patrimonio_db.pop(idx_item)
    
    # Registra no histórico a exclusão
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usuario_resp = st.session_state.get('username', 'admin')
    
    col_etiqueta = 'patrimonio' if 'patrimonio' in item_removido else 'etiqueta'
    col_nome = 'descricao' if 'descricao' in item_removido else 'nome'
    
    st.session_state.historico_db.append({
        "data": data_hora,
        "etiqueta": item_removido.get(col_etiqueta, 'N/I'),
        "item": item_removido.get(col_nome, 'Item'),
        "acao": "Exclusão de Patrimônio",
        "detalhes": f"Item excluído do sistema pelo usuário: {usuario_resp}",
        "foto": ""
    })

    # GRAVAÇÃO PERMANENTE NO BANCO DE DADOS/JSON
    if save_all_data:
        save_all_data(
            st.session_state.get('users_db', {}),
            st.session_state.get('patrimonio_db', []),
            st.session_state.get('historico_db', []),
            st.session_state.get('cidades_db', [])
        )
    
    st.success("Patrimônio excluído permanentemente com sucesso!")
    st.rerun()
