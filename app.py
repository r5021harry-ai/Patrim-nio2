import streamlit as st
import pandas as pd
from database.db import load_all_data
from services.auth import authenticate_user, create_user, update_password
from views.dashboard import render_dashboard
from views.gestao import render_gestao
from views.relatorios import render_relatorios

st.set_page_config(page_title="Patrimônio ISPN", page_icon="📦", layout="wide")

ISPN_LOGO_URL = "https://ispn.org.br/wp-content/uploads/2020/01/logo-ispn-30anos.png"

# Carregar dados
users_db, patrimonio_db, historico_db = load_all_data()

if "users_db" not in st.session_state:
    st.session_state.users_db = users_db
if "patrimonio_db" not in st.session_state:
    st.session_state.patrimonio_db = patrimonio_db
if "historico_db" not in st.session_state:
    st.session_state.historico_db = historico_db

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- LOGIN ---
def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 15px;">
                <img src="{ISPN_LOGO_URL}" width="180" alt="Logo ISPN" style="margin-bottom: 10px;">
                <h1 style="color: #2E7D32; font-family: 'Arial', sans-serif; font-size: 32px; font-weight: bold; margin-top: 5px;">
                    Patrimônio ISPN
                </h1>
                <p style="color: #666; font-size: 14px;">Instituto Sociedade, População e Natureza</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.markdown("---")
        with st.form("login_form"):
            u_input = st.text_input("Usuário")
            p_input = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar no Sistema", width="stretch"):
                ok, role = authenticate_user(st.session_state.users_db, u_input, p_input)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.username = u_input
                    st.session_state.role = role
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

if not st.session_state.logged_in:
    login_screen()
else:
    # Sidebar
    st.sidebar.image(ISPN_LOGO_URL, width=140)
    st.sidebar.markdown("### Patrimônio ISPN")
    st.sidebar.markdown(f"👤 Logado como: **{st.session_state.username}** (`{st.session_state.role.upper()}`)")
    if st.sidebar.button("🚪 Sair", width="stretch"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    st.sidebar.divider()

    if st.session_state.role == "admin":
        st.sidebar.subheader("⚙️ Configurações Admin")
        with st.sidebar.expander("🔑 Alterar minha senha"):
            with st.form("form_pass"):
                n_pass = st.text_input("Nova Senha", type="password")
                if st.form_submit_button("Atualizar Senha"):
                    if n_pass:
                        update_password(st.session_state.users_db, st.session_state.username, n_pass)
                        st.success("Senha alterada!")
                    else:
                        st.warning("Informe uma senha válida.")

        with st.sidebar.expander("➕ Cadastrar Novo Usuário"):
            with st.form("form_user"):
                n_user = st.text_input("Novo Usuário")
                n_pass = st.text_input("Senha", type="password")
                n_role = st.selectbox("Perfil", ["user", "admin"])
                if st.form_submit_button("Criar Usuário"):
                    if n_user and n_pass:
                        ok, msg = create_user(st.session_state.users_db, n_user, n_pass, n_role)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
                    else:
                        st.warning("Preencha todos os campos.")

    # Navegação das Páginas
    aba = st.tabs([
        "📊 Dashboard", 
        "➕ Cadastrar & Editar Patrimônio", 
        "📑 Relatórios & Importação"
    ])

    with aba[0]:
        render_dashboard(st.session_state.patrimonio_db)
    with aba[1]:
        render_gestao(st.session_state.patrimonio_db, st.session_state.historico_db)
    with aba[2]:
        render_relatorios(st.session_state.patrimonio_db, st.session_state.historico_db)
