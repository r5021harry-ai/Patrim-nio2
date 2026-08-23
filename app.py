import streamlit as st
import os
import pandas as pd
import importlib

# Importação flexível do módulo de Banco de Dados
try:
    db_mod = importlib.import_module("banco de dados.db")
except ModuleNotFoundError:
    try:
        db_mod = importlib.import_module("banco_dados.db")
    except ModuleNotFoundError:
        db_mod = importlib.import_module("database.db")

load_all_data = getattr(db_mod, "load_all_data", getattr(db_mod, "cargar_todos_os_dados", None))

# Importação flexível dos Serviços
try:
    auth_mod = importlib.import_module("serviços.auth")
except ModuleNotFoundError:
    try:
        auth_mod = importlib.import_module("servicos.auth")
    except ModuleNotFoundError:
        auth_mod = importlib.import_module("services.auth")

authenticate_user = auth_mod.authenticate_user
create_user = auth_mod.create_user
update_password = auth_mod.update_password

# Importação flexível das Visualizações (Vistas)
try:
    dash_mod = importlib.import_module("vistas.dashboard")
    gest_mod = importlib.import_module("vistas.gestao")
    rel_mod = importlib.import_module("vistas.relatorios")
except ModuleNotFoundError:
    dash_mod = importlib.import_module("views.dashboard")
    gest_mod = importlib.import_module("views.gestao")
    rel_mod = importlib.import_module("views.relatorios")

render_dashboard = dash_mod.render_dashboard
render_gestao = gest_mod.render_gestao
render_relatorios = rel_mod.render_relatorios

st.set_page_config(page_title="Patrimônio ISPN", page_icon="📦", layout="wide")

# Caminho da Logo
LOGO_PATH = "logo.png" if os.path.exists("logo.png") else "https://ispn.org.br/wp-content/uploads/2020/01/logo-ispn-30anos.png"

# Carregar dados
data = load_all_data()
if len(data) == 4:
    users_db, patrimonio_db, historico_db, cidades_db = data
else:
    users_db, patrimonio_db, historico_db = data
    cidades_db = {"lista": ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"], "padrao": "Santa Inês – MA"}

if "users_db" not in st.session_state: st.session_state.users_db = users_db
if "patrimonio_db" not in st.session_state: st.session_state.patrimonio_db = patrimonio_db
if "historico_db" not in st.session_state: st.session_state.historico_db = historico_db
if "cidades_db" not in st.session_state: st.session_state.cidades_db = cidades_db

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- TELA DE LOGIN ---
def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image(LOGO_PATH, width=200)
        except Exception:
            pass
            
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 15px;">
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
            if st.form_submit_button("Entrar no Sistema", use_container_width=True):
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
    try:
        st.sidebar.image(LOGO_PATH, width=140)
    except Exception:
        pass
        
    st.sidebar.markdown("### Patrimônio ISPN")
    st.sidebar.markdown(f"👤 Logado como: **{st.session_state.username}** (`{st.session_state.role.upper()}`)")
    if st.sidebar.button("🚪 Sair", use_container_width=True):
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

    # Aba Navegação
    aba = st.tabs([
        "📊 Dashboard", 
        "➕ Cadastrar & Editar Patrimônio", 
        "📑 Relatórios & Importação"
    ])

    with aba[0]:
        render_dashboard(st.session_state.patrimonio_db)
    with aba[1]:
        try:
            render_gestao(st.session_state.patrimonio_db, st.session_state.historico_db, st.session_state.cidades_db)
        except TypeError:
            render_gestao(st.session_state.patrimonio_db, st.session_state.historico_db)
            
    with aba[2]:
        try:
            render_relatorios(st.session_state.patrimonio_db, st.session_state.historico_db, st.session_state.cidades_db)
        except TypeError:
            render_relatorios(st.session_state.patrimonio_db, st.session_state.historico_db)
