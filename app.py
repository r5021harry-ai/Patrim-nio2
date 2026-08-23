import streamlit as st
import os
import pandas as pd

from banco_dados.db import load_all_data
from servicos.auth import authenticate_user, create_user, update_password
from vistas.dashboard import render_dashboard
from vistas.gestao import render_gestao
from vistas.relatorios import render_relatorios

st.set_page_config(page_title="Patrimônio ISPN", page_icon="📦", layout="wide")

LOGO_PATH = "logo.png" if os.path.exists("logo.png") else "https://ispn.org.br/wp-content/uploads/2020/01/logo-ispn-30anos.png"

# Carregar dados
users_db, patrimonio_db, historico_db = load_all_data()

if "users_db" not in st.session_state: st.session_state.users_db = users_db
if "patrimonio_db" not in st.session_state: st.session_state.patrimonio_db = patrimonio_db
if "historico_db" not in st.session_state: st.session_state.historico_db = historico_db
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# Tela de Login
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=200)
        st.markdown("<h2 style='text-align: center; color: #2E7D32;'>Patrimônio ISPN</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u_input = st.text_input("Usuário")
            p_input = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar no Sistema", use_container_width=True):
                ok, role = authenticate_user(st.session_state.users_db, u_input, p_input)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.username = u_input
                    st.session_state.role = role
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
else:
    # Sidebar
    if os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, width=140)
    st.sidebar.markdown(f"👤 Logado como: **{st.session_state.username}**")
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # Páginas
    aba = st.tabs(["📊 Dashboard", "➕ Cadastrar & Editar Patrimônio", "📑 Relatórios & Importação"])
    with aba[0]: render_dashboard(st.session_state.patrimonio_db)
    with aba[1]: render_gestao(st.session_state.patrimonio_db, st.session_state.historico_db)
    with aba[2]: render_relatorios(st.session_state.patrimonio_db, st.session_state.historico_db)
