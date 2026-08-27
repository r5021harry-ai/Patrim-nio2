import streamlit as st
import os
import pandas as pd
import importlib
import io
import tempfile
from PIL import Image

# Importações para geração de PDF e QR Code (fpdf + qrcode)
from fpdf import FPDF
import qrcode

# --- CAMINHO DA LOGO ATUALIZADO ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "ispn2.png")

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Patrimônio ISPN", 
    page_icon="ispn2.png" if os.path.exists("ispn2.png") else "images.jpg", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- REGRAS CSS: TEMA CLARO HARMONIZADO ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root { color-scheme: light !important; }

    html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }

    .stApp { background-color: #FFFFFF !important; }

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

    input, select, textarea, 
    [data-baseweb="input"], 
    [data-baseweb="base-input"],
    [data-testid="stSidebar"] input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px !important;
    }

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
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES DE QR CODE E ETIQUETA ---
def gerar_qrcode(conteudo_str):
    """Gera o buffer de imagem PNG do QR Code contendo as informações/etiqueta."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=1,
    )
    qr.add_data(conteudo_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    rv = io.BytesIO()
    img.save(rv, format="PNG")
    rv.seek(0)
    return rv

def gerar_pdf_etiqueta(codigo_etiqueta):
    """Gera PDF de etiqueta (50x30mm) fiel ao modelo físico (Logo na esquerda | QR Code e Patrimônio na direita)."""
    pdf = FPDF(orientation='L', unit='mm', format=(30, 50))
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    
    # Borda fina e discreta
    pdf.set_line_width(0.2)
    pdf.set_draw_color(200, 200, 200)
    pdf.rect(1, 1, 48, 28)

    # 1. ESQUERDA: LOGO COMPLETA (ispn2.png)
    if os.path.exists(LOGO_PATH):
        try:
            pdf.image(LOGO_PATH, x=3, y=4, w=22)
        except Exception:
            pass

    # 2. DIREITA: TEXTO 'Patrimônio', QR CODE E CÓDIGO
    pdf.set_xy(26, 3)
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(70, 70, 70)
    pdf.cell(21, 4, "Patrimônio", 0, 1, 'C')

    # QR Code
    etiqueta_str = str(codigo_etiqueta)
    qr_buffer = gerar_qrcode(etiqueta_str)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        tmp.write(qr_buffer.getvalue())
        tmp_path = tmp.name

    pdf.image(tmp_path, x=29.5, y=7.5, w=14, h=14)

    # Número da Etiqueta
    pdf.set_xy(26, 22)
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(21, 4, etiqueta_str, 0, 1, 'C')
    
    try:
        os.remove(tmp_path)
    except Exception:
        pass

    return bytes(pdf.output(dest='S'))

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
delete_user = getattr(auth_mod, "delete_user", None)

# --- IMPORTAÇÃO E RECARREGAMENTO DINÂMICO DAS VIEWS ---
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

importlib.reload(dash_mod)
importlib.reload(gest_mod)
importlib.reload(rel_mod)
importlib.reload(conf_mod)

render_dashboard = dash_mod.render_dashboard
render_gestao = gest_mod.render_gestao
render_relatorios = rel_mod.render_relatorios
render_conferencia = conf_mod.render_conferencia

# --- FUNÇÃO AUXILIAR DE PERSISTÊNCIA DE DADOS (CALLBACK) ---
def persistir_dados():
    if save_all_data:
        save_all_data(
            st.session_state.users_db,
            st.session_state.patrimonio_db,
            st.session_state.historico_db,
            st.session_state.cidades_db
        )

# --- CARREGAMENTO DE DADOS E GARANTIA FORÇADA DE ADMIN ---
if "patrimonio_db" not in st.session_state:
    if load_all_data:
        data = load_all_data()
        if isinstance(data, tuple) and len(data) == 4:
            users_db, patrimonio_db, historico_db, cidades_db = data
        elif isinstance(data, tuple) and len(data) == 3:
            users_db, patrimonio_db, historico_db = data
            cidades_db = {"lista": ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"], "padrao": "Santa Inês – MA"}
        else:
            users_db, patrimonio_db, historico_db, cidades_db = {}, [], [], {"lista": ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"], "padrao": "Santa Inês – MA"}
    else:
        users_db, patrimonio_db, historico_db, cidades_db = {}, [], [], {"lista": ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"], "padrao": "Santa Inês – MA"}

    if "admin" not in users_db:
        create_user(users_db, "admin", "123", role="admin")
    else:
        update_password(users_db, "admin", "123")
        if isinstance(users_db.get("admin"), dict):
            users_db["admin"]["role"] = "admin"

    if save_all_data:
        save_all_data(users_db, patrimonio_db, historico_db, cidades_db)

    st.session_state.users_db = users_db
    st.session_state.patrimonio_db = patrimonio_db
    st.session_state.historico_db = historico_db
    st.session_state.cidades_db = cidades_db

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- TELA DE LOGIN ---
def login_screen():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("ispn2.png"):
            img_c1, img_c2, img_c3 = st.columns([1, 2, 1])
            with img_c2:
                st.image("ispn2.png", use_container_width=True)
                
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
            
            submitted = st.form_submit_button("Entrar no Sistema", use_container_width=True, type="primary")
            if submitted:
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
        if os.path.exists("ispn2.png"):
            side_c1, side_c2, side_c3 = st.columns([1, 2, 1])
            with side_c2:
                st.image("ispn2.png", use_container_width=True)
                
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
        
        if st.button("Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

        st.divider()

        # --- PAINEL DO ADMIN ---
        if st.session_state.role == "admin":
            st.markdown("<p style='color: #15803D; font-weight: 700; font-size: 13px; text-transform: uppercase;'> PAINEL ADMIN</p>", unsafe_allow_html=True)
            
            with st.expander("Controle de Usuários e Logins"):
                dict_users = st.session_state.get("users_db", {})
                
                if dict_users:
                    user_list = list(dict_users.keys())
                    u_sel = st.selectbox("Selecione um usuário:", user_list)
                    
                    if u_sel:
                        u_data = dict_users[u_sel]
                        u_role = u_data.get("role", "user") if isinstance(u_data, dict) else ("admin" if u_sel == "admin" else "user")
                        st.caption(f"Perfil atual: **{u_role}**")
                        
                        n_pass_adm = st.text_input(f"Nova senha para {u_sel}", type="password", key=f"p_{u_sel}")
                        if st.button("Salvar Nova Senha", key=f"btn_p_{u_sel}", type="primary"):
                            if n_pass_adm:
                                update_password(st.session_state.users_db, u_sel, n_pass_adm)
                                persistir_dados()
                                st.success("Senha alterada com sucesso!")
                            else:
                                st.warning("Digite uma senha válida.")

                        st.markdown("---")
                        
                        if u_sel == st.session_state.username:
                            st.info("Você não pode apagar seu próprio usuário conectado.")
                        else:
                            if st.button(f"Apagar Usuário '{u_sel}'", key=f"del_{u_sel}"):
                                if delete_user:
                                    delete_user(st.session_state.users_db, u_sel)
                                else:
                                    st.session_state.users_db.pop(u_sel, None)
                                
                                persistir_dados()
                                st.success(f"Usuário '{u_sel}' removido!")
                                st.rerun()

            with st.expander("Cadastrar Novo Usuário"):
                with st.form("form_novo_user"):
                    n_user = st.text_input("Usuário (ex: joao)")
                    n_pass = st.text_input("Senha", type="password")
                    n_role = st.selectbox("Perfil", ["user", "admin"])
                    if st.form_submit_button("Criar Usuário", type="primary"):
                        if n_user and n_pass:
                            ok, msg = create_user(st.session_state.users_db, n_user, n_pass, n_role)
                            if ok:
                                persistir_dados()
                                st.success(msg)
                            else:
                                st.error(msg)

            with st.expander("Gerenciar Dados"):
                if st.button("Limpar Histórico Geral", type="primary", use_container_width=True):
                    st.session_state.historico_db = []
                    persistir_dados()
                    st.success("Histórico limpo!")
                    st.rerun()

    # --- ÁREA PRINCIPAL ---
    aba = st.tabs([
        "Dashboard Geral", 
        "Gestão de Patrimônio", 
        "Conferência / Auditoria", 
        "Emissão de Etiquetas", 
        "Relatórios"
    ])
    
    with aba[0]:
        render_dashboard(st.session_state.patrimonio_db)

    with aba[1]:
        try:
            render_gestao(
                st.session_state.patrimonio_db, 
                st.session_state.historico_db, 
                st.session_state.cidades_db, 
                save_callback=persistir_dados
            )
        except TypeError:
            try:
                render_gestao(
                    st.session_state.patrimonio_db, 
                    st.session_state.historico_db, 
                    save_callback=persistir_dados
                )
            except TypeError:
                render_gestao(st.session_state.patrimonio_db, st.session_state.historico_db)
            
        st.markdown("<br><hr>", unsafe_allow_html=True)
        
        # --- SEÇÃO DE IMPORTAÇÃO DE PLANILHA NA ABA GESTÃO ---
        with st.expander("Importar Planilha de Patrimônio (Excel / CSV)", expanded=False):
            st.markdown("### Orientações sobre a Formatação da Planilha")
            st.markdown("""
            Para garantir que o sistema reconheça corretamente todas as informações, a primeira linha da sua planilha deve conter **exatamente os nomes de colunas (cabeçalho)** listados abaixo:
            """)
            
            exemplo_df = pd.DataFrame([
                {
                    "etiqueta": "PAT001",
                    "nome": "Notebook Dell Vostro",
                    "categoria": "Informática",
                    "localizacao": "Santa Inês – MA",
                    "responsavel": "João Silva",
                    "estado": "Bom",
                    "placa": ""
                },
                {
                    "etiqueta": "VEI001",
                    "nome": "Toyota Hilux 4x4",
                    "categoria": "Veículos",
                    "localizacao": "Sede DF",
                    "responsavel": "Maria Santos",
                    "estado": "Novo",
                    "placa": "ABC-1234"
                }
            ])
            st.dataframe(exemplo_df, use_container_width=True, hide_index=True)
            
            st.markdown("""
            **Detalhamento dos Campos Recomendados:**
            * **`etiqueta`** *(Obrigatório)*: Código único identificador do patrimônio (Ex: `PAT001`, `10025`).
            * **`nome`** *(Obrigatório)*: Descrição ou nome do item (Ex: `Impressora HP`, `Toyota Hilux`).
            * **`categoria`**: Categoria do bem (Ex: `Informática`, `Mobiliário`, `Veículos`).
            * **`localizacao`**: Local físico onde o bem se encontra (Ex: `Santa Inês – MA`, `Sede DF`).
            * **`responsavel`**: Pessoa responsável pelo bem.
            * **`estado`**: Condição do bem (Ex: `Novo`, `Bom`, `Manutenção`, `Inservível`).
            * **`placa`** *(Opcional)*: Placa do veículo (Recomendado para a categoria **Veículos**).
            
            ---
            """)
            
            buffer_modelo = io.BytesIO()
            with pd.ExcelWriter(buffer_modelo, engine='openpyxl') as writer:
                exemplo_df.to_excel(writer, index=False, sheet_name='Modelo')
            buffer_modelo.seek(0)

            st.download_button(
                label="Baixar Planilha Modelo (.xlsx)",
                data=buffer_modelo,
                file_name="modelo_importacao_patrimonio.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            arquivo_upload = st.file_uploader("Carregue seu arquivo de planilha (.xlsx ou .csv):", type=["csv", "xlsx"])
            
            if arquivo_upload is not None:
                try:
                    if arquivo_upload.name.endswith('.csv'):
                        df_import = pd.read_csv(arquivo_upload)
                    else:
                        df_import = pd.read_excel(arquivo_upload)
                    
                    st.write("Pré-visualização dos Dados Importados:")
                    st.dataframe(df_import.head(10), use_container_width=True)
                    
                    mod_import = st.radio(
                        "Escolha a forma de importação:", 
                        ["Adicionar à base existente (Recomendado)", "Substituir base inteira"]
                    )
                    
                    if st.button("Confirmar Importação", type="primary"):
                        df_import = df_import.fillna("")
                        novos_itens = df_import.to_dict(orient="records")
                        
                        if mod_import == "Substituir base inteira":
                            st.session_state.patrimonio_db = novos_itens
                        else:
                            st.session_state.patrimonio_db.extend(novos_itens)
                            
                        persistir_dados()
                        
                        st.success(f"Importação realizada com sucesso! {len(novos_itens)} itens adicionados/atualizados.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao ler e importar o arquivo: {str(e)}")

    with aba[2]:
        try:
            render_conferencia(
                st.session_state.patrimonio_db, 
                st.session_state.historico_db, 
                st.session_state.cidades_db, 
                save_callback=persistir_dados
            )
        except TypeError:
            try:
                render_conferencia(
                    st.session_state.patrimonio_db, 
                    st.session_state.historico_db, 
                    save_callback=persistir_dados
                )
            except TypeError:
                render_conferencia(st.session_state.patrimonio_db, st.session_state.historico_db)

    # --- ABA 3: EMISSÃO DE ETIQUETAS ---
    with aba[3]:
        st.subheader("Gerador de Etiquetas Patrimoniais")
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

            col_sel1, _ = st.columns([2, 1])
            with col_sel1:
                opcoes_itens = df_patrimonio[col_etiqueta].astype(str) + " - " + df_patrimonio[col_nome].astype(str)
                item_selecionado = st.selectbox("Selecione o Patrimônio:", opcoes_itens, key="aba_etiquetas_select")
            
            if item_selecionado and isinstance(item_selecionado, str) and " - " in item_selecionado:
                etiqueta_cod = item_selecionado.split(" - ")[0].strip()
                item_dados_lista = df_patrimonio[df_patrimonio[col_etiqueta].astype(str).str.strip() == etiqueta_cod]
                
                if not item_dados_lista.empty:
                    item_dados = item_dados_lista.iloc[0].to_dict()
                    st.markdown("---")
                    
                    c_etiqueta, c_info = st.columns([1, 1.2])
                    
                    # PREVISÃO DA ETIQUETA NA TELA
                    with c_etiqueta:
                        qr_buffer = gerar_qrcode(etiqueta_cod)
                        
                        with st.container(border=True):
                            col_logo, col_qr = st.columns([1.1, 1])

                            with col_logo:
                                if os.path.exists(LOGO_PATH):
                                    st.image(LOGO_PATH, use_container_width=True)

                            with col_qr:
                                st.markdown("<p style='text-align: center; color: #555; margin: 0; font-size: 13px;'>Patrimônio</p>", unsafe_allow_html=True)
                                st.image(qr_buffer, use_container_width=True)
                                st.markdown(f"<p style='text-align: center; font-weight: bold; margin: 0; font-size: 14px; color: #000;'>{etiqueta_cod}</p>", unsafe_allow_html=True)

                        pdf_bytes = gerar_pdf_etiqueta(etiqueta_cod)

                        st.download_button(
                            label="Baixar Etiqueta em PDF (50x30mm)",
                            data=pdf_bytes,
                            file_name=f"etiqueta_{etiqueta_cod}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary",
                            key="btn_download_etiqueta_aba3"
                        )

                    with c_info:
                        st.markdown(f"**Código:** `{etiqueta_cod}`")
                        st.markdown(f"**Item:** {item_dados.get(col_nome, 'N/A')}")
                        for key, val in item_dados.items():
                            if key not in [col_etiqueta, col_nome]:
                                st.markdown(f"**{str(key).title()}:** {val}")
        else:
            st.info("Nenhum patrimônio disponível.")

    with aba[4]:
        try:
            render_relatorios(st.session_state.patrimonio_db, st.session_state.historico_db, st.session_state.cidades_db)
        except TypeError:
            render_relatorios(st.session_state.patrimonio_db, st.session_state.historico_db)
