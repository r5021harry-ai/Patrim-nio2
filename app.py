import streamlit as st
import os
import pandas as pd
import importlib

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Patrimônio ISPN", 
    page_icon="📦", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOMIZADO (LIMPO E CORRIGIDO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #0E1318;
    }

    /* Cards de Métricas */
    [data-testid="stMetric"] {
        background: #141B21;
        border: 1px solid #2A363F;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    /* Estilização das Abas (Tabs) Sem Fundo Verde */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        background-color: transparent;
        padding: 0;
        border-bottom: 1px solid #2A363F;
    }

    .stTabs [data-baseweb="tab"] {
        height: 40px;
        background-color: transparent !important;
        border: none !important;
        color: #9CA3AF !important;
        font-weight: 500;
        font-size: 0.95rem;
        padding: 0px 8px;
    }

    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #2E7D32 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #141B21;
        border-right: 1px solid #2A363F;
    }

    /* Botões Padrão */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        border: 1px solid #2A363F;
        background-color: #1A232A;
        color: #E2E8F0;
    }

    .stButton>button[kind="primary"] {
        background: #2E7D32;
        border: none;
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# --- IMPORTAÇÕES INTELIGENTES ---
try:
    db_mod = importlib.import_module("banco de dados.db")
except ModuleNotFoundError:
    try:
        db_mod = importlib.import_module("banco_dados.db")
    except ModuleNotFoundError:
        db_mod = importlib.import_module("database.db")

load_all_data = getattr(db_mod, "load_all_data", getattr(db_mod, "cargar_todos_os_dados", None))
save_all_data = getattr(db_mod, "save_all_data", getattr(db_mod, "guardar_todos_os_dados", None))

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

# --- CARREGAMENTO DE DADOS ---
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

# --- TELA DE LOGIN CORRIGIDA ---
def login_screen():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"):
            img_c1, img_c2, img_c3 = st.columns([1, 2, 1])
            with img_c2:
                st.image("logo.png", use_container_width=True)
                
        st.markdown(
            """
            <div style="text-align: center; margin-top: 10px; margin-bottom: 20px;">
                <h2 style="color: #FFFFFF; font-weight: 700; margin-bottom: 4px; font-size: 26px;">
                    Patrimônio ISPN
                </h2>
                <p style="color: #9CA3AF; font-size: 13px; margin: 0;">Instituto Sociedade, População e Natureza</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        with st.form("login_form"):
            u_input = st.text_input("Usuário")
            p_input = st.text_input("Senha", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Entrar no Sistema", use_container_width=True, type="primary"):
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
    # --- SIDEBAR ---
    with st.sidebar:
        if os.path.exists("logo.png"):
            side_c1, side_c2, side_c3 = st.sidebar.columns([1, 2, 1])
            with side_c2:
                st.image("logo.png", use_container_width=True)
                
        st.markdown(
            f"""
            <div style='text-align: center; margin-top: 10px; margin-bottom: 15px; background: #1A232A; padding: 10px; border-radius: 8px; border: 1px solid #2A363F;'>
                <span style='color: #9CA3AF; font-size: 12px;'>Conectado como</span><br>
                <b style='color: #E2E8F0; font-size: 14px;'>{st.session_state.username}</b> 
                <span style='background-color: #2E7D32; color: #FFF; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: bold;'>{st.session_state.role.upper()}</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

        st.divider()

        # Painel do Administrador
        if st.session_state.role == "admin":
            st.markdown("<p style='color: #2E7D32; font-weight: 700; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;'> Painel Admin</p>", unsafe_allow_html=True)
            
            with st.expander("🔑 Alterar minha senha"):
                with st.form("form_pass"):
                    n_pass = st.text_input("Nova Senha", type="password")
                    if st.form_submit_button("Atualizar"):
                        if n_pass:
                            update_password(st.session_state.users_db, st.session_state.username, n_pass)
                            st.success("Senha alterada!")
                        else:
                            st.warning("Senha inválida.")

            with st.expander("➕ Cadastrar Novo Usuário"):
                with st.form("form_user"):
                    n_user = st.text_input("Novo Usuário")
                    n_pass = st.text_input("Senha", type="password")
                    n_role = st.selectbox("Perfil", ["user", "admin"])
                    if st.form_submit_button("Criar Usuário"):
                        if n_user and n_pass:
                            ok, msg = create_user(st.session_state.users_db, n_user, n_pass, n_role)
                            if ok: st.success(msg)
                            else: st.error(msg)

            with st.expander("🗑️ Gerenciar Dados"):
                if st.button("Limpar Histórico Geral", type="primary", use_container_width=True):
                    st.session_state.historico_db = []
                    if save_all_data:
                        save_all_data(st.session_state.users_db, st.session_state.patrimonio_db, [], st.session_state.cidades_db)
                    st.success("Histórico limpo com sucesso!")
                    st.rerun()

    # --- ÁREA PRINCIPAL DA APLICAÇÃO ---
    aba = st.tabs(["📊 Dashboard Geral", "📦 Gestão de Patrimônio", "📑 Relatórios & Importação"])
    
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
