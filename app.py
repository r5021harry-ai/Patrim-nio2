import streamlit as st
import os
import pandas as pd
import importlib
import urllib.parse
import io

# Importações para geração de PDF
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Patrimônio ISPN", 
    page_icon="📦", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- REGRAS CSS: TEMA CLARO HARMONIZADO ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        color-scheme: light !important;
    }

    /* Fundo Global */
    html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }

    .stApp {
        background-color: #FFFFFF !important;
    }

    /* BARRA LATERAL */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #0F172A !important;
    }

    /* EXPANDERS */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        margin-bottom: 8px !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] summary *,
    [data-testid="stSidebar"] [data-testid="stExpander"] summary span {
        color: #0F172A !important;
        font-weight: 600 !important;
    }

    /* INPUTS */
    input, select, textarea, 
    [data-baseweb="input"], 
    [data-baseweb="base-input"],
    [data-testid="stSidebar"] input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px !important;
    }

    /* MÉTRICAS SUPERIORES */
    [data-testid="stMetric"] {
        background: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }

    [data-testid="stMetricLabel"] *, [data-testid="stMetricLabel"] p {
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    [data-testid="stMetricValue"] *, [data-testid="stMetricValue"] div {
        color: #15803D !important;
        font-weight: 700 !important;
    }

    /* ABAS SUPERIORES */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        background-color: transparent;
        padding: 0;
        border-bottom: 2px solid #E2E8F0;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        background-color: transparent !important;
        border: none !important;
        color: #64748B !important;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0px 12px;
    }

    .stTabs [aria-selected="true"] {
        color: #15803D !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #15803D !important;
    }

    /* BOTÕES GERAIS */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }

    .stButton>button[kind="primary"] {
        background-color: #15803D !important;
        border: none !important;
        color: #FFFFFF !important;
    }

    .stButton>button[kind="primary"]:hover {
        background-color: #166534 !important;
    }

    /* ETIQUETA CARD */
    .etiqueta-card {
        background: #FFFFFF !important;
        color: #000000 !important;
        padding: 18px;
        border-radius: 10px;
        border: 2px solid #15803D;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- IMPORTAÇÕES INTELIGENTES DE MÓDULOS ---
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
    conf_mod = importlib.import_module("vistas.conferencia")
except ModuleNotFoundError:
    dash_mod = importlib.import_module("views.dashboard")
    gest_mod = importlib.import_module("views.gestao")
    rel_mod = importlib.import_module("views.relatorios")
    conf_mod = importlib.import_module("views.conferencia")

render_dashboard = dash_mod.render_dashboard
render_gestao = gest_mod.render_gestao
render_relatorios = rel_mod.render_relatorios
render_conferencia = conf_mod.render_conferencia

# --- FUNÇÃO PARA GERAR O PDF DA ETIQUETA ---
def gerar_pdf_etiqueta(codigo, nome_item):
    buffer = io.BytesIO()
    largura = 50 * mm
    altura = 30 * mm
    
    c = canvas.Canvas(buffer, pagesize=(largura, altura))
    c.setFont("Helvetica-Bold", 7)
    c.setFillColorRGB(0.09, 0.50, 0.24)
    c.drawCentredString(largura / 2.0, altura - 5 * mm, "PATRIMÔNIO ISPN")
    
    c.setFont("Helvetica-Bold", 6)
    c.setFillColorRGB(0, 0, 0)
    nome_curto = (nome_item[:20] + '...') if len(str(nome_item)) > 20 else str(nome_item)
    c.drawCentredString(largura / 2.0, altura - 9 * mm, nome_curto)
    
    barcode = code128.Code128(codigo, barHeight=11 * mm, barWidth=0.28 * mm)
    barcode.drawOn(c, (largura - barcode.width) / 2.0, 7 * mm)
    
    c.setFont("Helvetica", 6)
    c.drawCentredString(largura / 2.0, 3 * mm, f"Etiqueta: {codigo}")
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer.getvalue()

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

# --- TELA DE LOGIN ---
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
                <h2 style="color: #15803D; font-weight: 700; margin-bottom: 4px; font-size: 26px;">
                    Patrimônio ISPN
                </h2>
                <p style="color: #64748B; font-size: 13px; margin: 0;">Instituto Sociedade, População e Natureza</p>
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
    # --- SIDEBAR HARMONIZADA ---
    with st.sidebar:
        if os.path.exists("logo.png"):
            side_c1, side_c2, side_c3 = st.columns([1, 2, 1])
            with side_c2:
                st.image("logo.png", use_container_width=True)
                
        st.markdown(
            f"""
            <div style='text-align: center; margin-top: 10px; margin-bottom: 15px; background: #FFFFFF; padding: 12px; border-radius: 8px; border: 1px solid #CBD5E1;'>
                <span style='color: #64748B; font-size: 12px;'>Conectado como</span><br>
                <b style='color: #0F172A; font-size: 14px;'>{st.session_state.username}</b> 
                <span style='background-color: #15803D; color: #FFFFFF; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: bold;'>{st.session_state.role.upper()}</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

        st.divider()

        if st.session_state.role == "admin":
            st.markdown("<p style='color: #15803D; font-weight: 700; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;'> PAINEL ADMIN</p>", unsafe_allow_html=True)
            
            with st.expander("🔑 Alterar minha senha"):
                with st.form("form_pass"):
                    n_pass = st.text_input("Nova Senha", type="password")
                    if st.form_submit_button("Atualizar", type="primary"):
                        if n_pass:
                            update_password(st.session_state.users_db, st.session_state.username, n_pass)
                            st.success("Senha alterada!")
                        else:
                            st.warning("Senha inválida.")

            with st.expander("➕ Cadastrar Novo Usuário"):
                with st.form("form_user"):
                    n_user = st.text_input("Novo Usuário (ex: funcionario1)")
                    n_pass = st.text_input("Senha", type="password")
                    n_role = st.selectbox("Perfil", ["user", "admin"])
                    if st.form_submit_button("Criar Usuário", type="primary"):
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
    aba = st.tabs([
        "📊 Dashboard Geral", 
        "📦 Gestão de Patrimônio", 
        "📱 Conferência / Auditoria", 
        "🏷️ Emissão de Etiquetas", 
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
            render_conferencia(st.session_state.patrimonio_db, st.session_state.historico_db, st.session_state.cidades_db)
        except TypeError:
            render_conferencia(st.session_state.patrimonio_db, st.session_state.historico_db)

    with aba[3]:
        st.subheader("🏷️ Gerador de Etiquetas Patrimoniais")
        
        df_patrimonio = pd.DataFrame(st.session_state.patrimonio_db)
        
        if not df_patrimonio.empty:
            col_etiqueta = 'etiqueta' if 'etiqueta' in df_patrimonio.columns else (
                'patrimonio' if 'patrimonio' in df_patrimonio.columns else df_patrimonio.columns[0]
            )
            
            col_nome = 'nome' if 'nome' in df_patrimonio.columns else (
                'item' if 'item' in df_patrimonio.columns else (
                    'descricao' if 'descricao' in df_patrimonio.columns else df_patrimonio.columns[1] if len(df_patrimonio.columns) > 1 else col_etiqueta
                )
            )

            col_sel1, col_sel2 = st.columns([2, 1])
            with col_sel1:
                opcoes_itens = df_patrimonio[col_etiqueta].astype(str) + " - " + df_patrimonio[col_nome].astype(str)
                item_selecionado = st.selectbox("Selecione o Patrimônio:", opcoes_itens)
            
            if item_selecionado and isinstance(item_selecionado, str) and " - " in item_selecionado:
                etiqueta_cod = item_selecionado.split(" - ")[0]
                item_dados_lista = df_patrimonio[df_patrimonio[col_etiqueta].astype(str) == etiqueta_cod]
                
                if not item_dados_lista.empty:
                    item_dados = item_dados_lista.iloc[0]
                    item_titulo = str(item_dados[col_nome])
                    
                    barcode_url = f"https://barcode.tec-it.com/barcode.ashx?data={urllib.parse.quote(etiqueta_cod)}&code=Code128&translate-esc=false"
                    
                    st.markdown("---")
                    c_etiqueta, c_info = st.columns([1, 2])
                    
                    with c_etiqueta:
                        st.markdown(
                            f"""
                            <div class="etiqueta-card">
                                <h3 style="margin: 0; color: #15803D; font-size: 18px;">PATRIMÔNIO ISPN</h3>
                                <p style="margin: 5px 0; font-weight: bold; font-size: 16px;">{item_titulo}</p>
                                <img src="{barcode_url}" alt="Código de Barras" style="width: 80%; margin: 10px 0;">
                                <p style="margin: 0; font-size: 12px; color: #555;">Etiqueta: {etiqueta_cod}</p>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )

                        pdf_bytes = gerar_pdf_etiqueta(etiqueta_cod, item_titulo)

                        st.download_button(
                            label="📄 Baixar Etiqueta em PDF (50x30mm)",
                            data=pdf_bytes,
                            file_name=f"etiqueta_{etiqueta_cod}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary"
                        )

                    with c_info:
                        st.markdown(f"**Código:** `{etiqueta_cod}`")
                        st.markdown(f"**Item:** {item_titulo}")
                        for key, val in item_dados.items():
                            if key not in [col_etiqueta, col_nome]:
                                st.markdown(f"**{str(key).title()}:** {val}")
        else:
            st.info("Nenhum patrimônio disponível no banco de dados para gerar etiquetas.")

    with aba[4]:
        try:
            render_relatorios(st.session_state.patrimonio_db, st.session_state.historico_db, st.session_state.cidades_db)
        except TypeError:
            render_relatorios(st.session_state.patrimonio_db, st.session_state.historico_db)
