import streamlit as st
import pandas as pd
from datetime import datetime
import importlib
import base64
import io
import pytz

# Configuração do fuso horário do Brasil
TZ_BR = pytz.timezone("America/Sao_Paulo")

def obter_agora_br():
    """Retorna o datetime atual formatado no fuso horário do Brasil."""
    return datetime.now(TZ_BR)

# Importações para geração de PDF com ReportLab
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

# Tenta importar bibliotecas de leitura de código de barras e imagem
try:
    from PIL import Image as PILImage
    import cv2
    import numpy as np
    HAS_VISION = True
except ImportError:
    HAS_VISION = False

try:
    from pyzbar.pyzbar import decode as decode_barcode
    HAS_PYZBAR = True
except ImportError:
    HAS_PYZBAR = False

# Tenta importar salvamento do banco de dados
try:
    db_mod = importlib.import_module("banco de dados.db")
except ModuleNotFoundError:
    try:
        db_mod = importlib.import_module("banco_dados.db")
    except ModuleNotFoundError:
        db_mod = importlib.import_module("database.db")

save_all_data = getattr(db_mod, "save_all_data", getattr(db_mod, "guardar_todos_os_dados", None))

def ler_codigo_imagem(image_file):
    """Extrai código de barras de uma foto capturada pela câmera."""
    if not HAS_VISION or not HAS_PYZBAR:
        return None
    try:
        img = PILImage.open(image_file)
        decoded_objs = decode_barcode(img)
        for obj in decoded_objs:
            return obj.data.decode("utf-8").strip()
    except Exception:
        pass
    return None

def formatar_data_vistoria_br(data_orig):
    """
    Trata e converte qualquer formato de data/hora salvo no banco 
    para o fuso horário oficial do Brasil (America/Sao_Paulo).
    """
    if not data_orig:
        return "N/A"
    
    data_str = str(data_orig).strip()
    
    try:
        # Se já tiver "às", apenas retorna se for válido
        if "às" in data_str:
            return data_str

        # Tenta converter ISO / UTC string
        dt_obj = None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
            try:
                dt_obj = datetime.strptime(data_str.split(".")[0], fmt)
                break
            except ValueError:
                pass

        if dt_obj:
            # Se não tem timezone, assume UTC ou ajusta fuso BR caso necessário
            if dt_obj.tzinfo is None:
                # Converte para fuso de SP
                dt_utc = pytz.utc.localize(dt_obj)
                dt_br = dt_utc.astimezone(TZ_BR)
            else:
                dt_br = dt_obj.astimezone(TZ_BR)
            return dt_br.strftime("%d/%m/%Y às %H:%M:%S")
    except Exception:
        pass
        
    return data_str

def gerar_pdf_vistorias(lista_vistorias, patrimonio_db, col_etiqueta, titulo_relatorio="Relatório de Auditoria e Vistorias"):
    """Gera um PDF formatado contendo dados e fotos das vistorias mantendo proporções e fuso correto."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor("#1A365D"), alignment=1)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=9, leading=12, alignment=1, textColor=colors.gray)
    text_style = ParagraphStyle('TextStyle', parent=styles['Normal'], fontSize=9, leading=13)
    
    # Cabeçalho com Horário do momento de emissão do documento
    agora_br = obter_agora_br().strftime('%d/%m/%Y às %H:%M:%S')
    story.append(Paragraph(f"<b>{titulo_relatorio}</b>", title_style))
    story.append(Paragraph(f"Gerado em: {agora_br}", subtitle_style))
    story.append(Spacer(1, 15))

    for idx, vist in enumerate(reversed(lista_vistorias)):
        detalhes = vist.get("detalhes", "")
        partes = [p.strip() for p in detalhes.split("|")]
        dict_detalhes = {}
        for p in partes:
            if ":" in p:
                k, v = p.split(":", 1)
                dict_detalhes[k.strip()] = v.strip()

        # Busca Categoria
        categoria = "Não informada"
        item_bd = next((i for i in patrimonio_db if str(i.get(col_etiqueta, '')) == str(vist.get("etiqueta", ""))), None)
        if item_bd:
            categoria = item_bd.get("categoria", item_bd.get("tipo", "Não informada"))

        # Pega a data e hora EXATAS da VISTORIA e converte pro fuso do Brasil
        data_orig = vist.get('data', '')
        data_formatada = formatar_data_vistoria_br(data_orig)

        # Limpa emojis para evitar caracteres corrompidos no PDF
        estado = dict_detalhes.get('Estado', 'N/I')
        estado_limpo = estado.replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("⚠️", "").strip()

        # Texto das Informações
        info_text = f"""
        <b>Item:</b> {vist.get('item', 'N/I')}<br/>
        <b>Código/Patrimônio:</b> {vist.get('etiqueta', 'N/A')}<br/>
        <b>Categoria:</b> {categoria}<br/>
        <b>Data/Hora:</b> {data_formatada}<br/>
        <b>Estado de Conservação:</b> {estado_limpo}<br/>
        <b>Status:</b> {dict_detalhes.get('Status', 'N/I')}<br/>
        <b>Auditor:</b> {dict_detalhes.get('Auditor', 'N/I')}<br/>
        <b>Observações:</b> {dict_detalhes.get('Obs', 'Nenhuma')}
        """
        p_info = Paragraph(info_text, text_style)

        # Trata a foto proporcionalmente
        img_element = Paragraph("<i>Sem foto de comprovação</i>", text_style)
        foto = vist.get("foto") or vist.get("imagem")
        
        if foto:
            try:
                if isinstance(foto, str) and not foto.startswith("http"):
                    foto_bytes = base64.b64decode(foto)
                else:
                    foto_bytes = foto
                
                img_buffer = io.BytesIO(foto_bytes)
                
                if HAS_VISION:
                    pil_img = PILImage.open(img_buffer)
                    orig_w, orig_h = pil_img.size
                    
                    max_w, max_h = 140.0, 100.0
                    ratio = min(max_w / orig_w, max_h / orig_h)
                    new_w, new_h = orig_w * ratio, orig_h * ratio
                    
                    img_buffer.seek(0)
                    img_element = RLImage(img_buffer, width=new_w, height=new_h)
                else:
                    img_element = RLImage(img_buffer, width=130, height=100)
            except Exception:
                img_element = Paragraph("<i>Erro ao carregar imagem</i>", text_style)

        # Card de cada item no PDF
        tabela_card = Table([[p_info, img_element]], colWidths=[370, 150])
        tabela_card.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))

        story.append(tabela_card)
        story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def render_conferencia(patrimonio_db, historico_db, cidades_db=None):
    st.title("📱 Conferência e Auditoria de Patrimônio")
    st.caption("Faça a verificação de inventário escaneando a etiqueta ou digitando o código do bem.")

    if not patrimonio_db:
        st.warning("Nenhum patrimônio cadastrado no sistema.")
        return

    df = pd.DataFrame(patrimonio_db)
    
    col_etiqueta = 'patrimonio' if 'patrimonio' in df.columns else ('etiqueta' if 'etiqueta' in df.columns else df.columns[0])
    col_nome = 'descricao' if 'descricao' in df.columns else ('nome' if 'nome' in df.columns else ('item' if 'item' in df.columns else df.columns[1]))
    col_status = 'estado' if 'estado' in df.columns else ('status' if 'status' in df.columns else df.columns[2])
    col_local = 'cidade' if 'cidade' in df.columns else ('localizacao' if 'localizacao' in df.columns else df.columns[3])
    col_responsavel = 'usuario' if 'usuario' in df.columns else ('responsavel' if 'responsavel' in df.columns else df.columns[4])

    if "msg_conf_sucesso" in st.session_state:
        st.success(st.session_state.msg_conf_sucesso)
        del st.session_state.msg_conf_sucesso

    metodo = st.radio(
        "Como deseja identificar o patrimônio?",
        ["🔍 Digitar Código / Selecionar", "📷 Escanear Código via Câmera"],
        horizontal=True
    )

    codigo_buscado = ""

    if "Escanear" in metodo:
        st.info("Aponte a câmera do celular para o código de barras da etiqueta.")
        foto_barcode = st.camera_input("Capturar foto do Código de Barras")
        if foto_barcode:
            codigo_detectado = ler_codigo_imagem(foto_barcode)
            if codigo_detectado:
                st.success(f"Código identificado: **{codigo_detectado}**")
                codigo_buscado = codigo_detectado
            else:
                st.warning("Não foi possível ler o código de barras automaticamente. Digite o código manualmente abaixo.")
                codigo_buscado = st.text_input("Código do Item", key="code_manual_cam").strip()
    else:
        opcoes = [f"{item.get(col_etiqueta, '')} - {item.get(col_nome, '')}" for item in patrimonio_db]
        sel = st.selectbox("Selecione ou Digite o Patrimônio:", ["-- Digite ou Selecione --"] + opcoes)
        if sel != "-- Digite ou Selecione --":
            codigo_buscado = sel.split(" - ")[0]

    if codigo_buscado:
        idx = next((i for i, item in enumerate(patrimonio_db) if str(item.get(col_etiqueta, '')).upper() == codigo_buscado.upper()), None)
        
        if idx is None:
            st.error(f"Patrimônio com código **{codigo_buscado}** não foi encontrado no sistema.")
        else:
            item = patrimonio_db[idx]
            st.divider()
            
            st.subheader(f"📦 {item.get(col_nome, 'Item')} ({item.get(col_etiqueta, '')})")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Localização Atual", item.get(col_local, "N/I"))
            c2.metric("Status Atual", item.get(col_status, "N/I"))
            c3.metric("Responsável", item.get(col_responsavel, "Equipe ISPN"))

            st.markdown("---")
            st.markdown("### 📋 Formato de Vistoria / Auditoria")

            with st.form("form_auditoria"):
                col_f1, col_f2 = st.columns(2)
                
                with col_f1:
                    estado_conservacao = st.selectbox(
                        "Estado de Conservação do Bem *",
                        ["🟢 Ótimo Estado", "🟡 Precisa de Manutenção / Conserto", "🔴 Danificado / Inoperante", "⚠️ Não Localizado"]
                    )
                    
                    novo_status = st.selectbox(
                        "Atualizar Status no Sistema",
                        ["Disponível", "Em Uso", "Manutenção"],
                        index=0 if item.get(col_status) == "Disponível" else (1 if item.get(col_status) == "Em Uso" else 2)
                    )

                with col_f2:
                    obs = st.text_area("Observações da Vistoria", placeholder="Ex: Pneu dianteiro desgastado, arranhão na lateral...")
                    
                st.markdown("**📸 Foto de Comprovação da Vistoria (Opcional):**")
                
                opcao_foto = st.radio(
                    "Como deseja anexar a foto?",
                    ["📤 Enviar Foto do Arquivo", "📷 Tirar Foto Agora"],
                    horizontal=True,
                    key="radio_opcao_foto"
                )

                foto_vistoria = None
                if "Enviar Foto" in opcao_foto:
                    foto_vistoria = st.file_uploader("Selecione uma imagem (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"], key="upload_foto_file")
                else:
                    foto_vistoria = st.camera_input("Tirar Foto do Bem", key="foto_vistoria_cam")

                submit = st.form_submit_button("Registrar Conferência", type="primary", use_container_width=True)

                if submit:
                    # Captura exatamente a data/hora oficial no fuso horário do Brasil
                    data_hora = datetime.now(TZ_BR).strftime("%d/%m/%Y às %H:%M:%S")
                    usuario_auditor = st.session_state.get('username', 'usuario')

                    patrimonio_db[idx][col_status] = novo_status
                    patrimonio_db[idx]['ultimo_estado'] = estado_conservacao
                    patrimonio_db[idx]['ultima_vistoria'] = data_hora
                    patrimonio_db[idx]['vistoriado_por'] = usuario_auditor

                    foto_b64 = ""
                    if foto_vistoria is not None:
                        foto_bytes = foto_vistoria.getvalue()
                        foto_b64 = base64.b64encode(foto_bytes).decode('utf-8')

                    historico_db.append({
                        "data": data_hora,
                        "etiqueta": item.get(col_etiqueta),
                        "item": item.get(col_nome),
                        "acao": "Auditoria / Vistoria",
                        "detalhes": f"Estado: {estado_conservacao} | Status: {novo_status} | Obs: {obs} | Auditor: {usuario_auditor}",
                        "foto": foto_b64
                    })

                    if save_all_data:
                        users_db = st.session_state.get('users_db', {})
                        cidades = st.session_state.get('cidades_db', {})
                        save_all_data(users_db, patrimonio_db, historico_db, cidades)

                    st.session_state.msg_conf_sucesso = f"Conferência do item {item.get(col_etiqueta)} registrada com sucesso por {usuario_auditor}!"
                    st.rerun()

    # --- PAINEL DE VISTORIAS REALIZADAS ---
    st.divider()
    st.subheader("📸 Painel Exclusivo de Vistorias Realizadas")

    vistorias = [h for h in historico_db if "Vistoria" in h.get("acao", "") or "Auditoria" in h.get("acao", "")]

    if not vistorias:
        st.info("Nenhuma vistoria ou auditoria registrada até o momento.")
    else:
        categorias_set = set()
        vistorias_com_categoria = []

        for v in vistorias:
            cat = "Outros"
            item_bd = next((i for i in patrimonio_db if str(i.get(col_etiqueta, '')) == str(v.get("etiqueta", ""))), None)
            if item_bd:
                cat = item_bd.get("categoria", item_bd.get("tipo", "Outros"))
            categorias_set.add(cat)
            
            v_copy = dict(v)
            v_copy["categoria"] = cat
            vistorias_com_categoria.append(v_copy)

        # --- SEÇÃO DE DOWNLOAD DE RELATÓRIOS PDF ---
        col_down1, col_down2, col_down3 = st.columns([1, 1, 1], vertical_alignment="bottom")

        with col_down1:
            if HAS_REPORTLAB:
                pdf_total = gerar_pdf_vistorias(
                    vistorias, patrimonio_db, col_etiqueta, 
                    titulo_relatorio="Relatório Geral de Vistorias e Auditorias"
                )
                st.download_button(
                    label="📄 Baixar Toda a Auditoria (PDF)",
                    data=pdf_total,
                    file_name=f"auditoria_completa_{obter_agora_br().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.error("Instale 'reportlab' para baixar PDF (`pip install reportlab`).")

        with col_down2:
            lista_categorias = sorted(list(categorias_set))
            cat_selecionada = st.selectbox(
                "Selecionar Categoria para Baixar Vistoria/Auditoria:",
                lista_categorias,
                key="down_cat_pdf"
            )

        with col_down3:
            if HAS_REPORTLAB:
                vistorias_filtradas_cat = [v for v in vistorias_com_categoria if v["categoria"] == cat_selecionada]
                pdf_cat = gerar_pdf_vistorias(
                    vistorias_filtradas_cat, patrimonio_db, col_etiqueta, 
                    titulo_relatorio=f"Relatório de Vistorias - Categoria: {cat_selecionada}"
                )
                st.download_button(
                    label=f"📄 Baixar PDF ({cat_selecionada})",
                    data=pdf_cat,
                    file_name=f"vistorias_{cat_selecionada}_{obter_agora_br().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        st.markdown("---")

        # --- FILTRO EM TELA ---
        opcoes_filtro = ["-- Exibir Todos --"] + sorted(list(set(f"{h.get('etiqueta')} - {h.get('item')}" for h in vistorias if h.get('etiqueta'))))
        filtro_sel = st.selectbox("Filtrar por Código de Patrimônio na Tela:", opcoes_filtro)

        vistorias_exibicao = vistorias
        if filtro_sel != "-- Exibir Todos --":
            cod_filtro = filtro_sel.split(" - ")[0]
            vistorias_exibicao = [h for h in vistorias if str(h.get("etiqueta")) == cod_filtro]

        # --- CARDS VISUAIS NA TELA ---
        for vist in reversed(vistorias_exibicao):
            with st.container():
                col_info, col_img = st.columns([3, 1])

                detalhes = vist.get("detalhes", "")
                partes = [p.strip() for p in detalhes.split("|")]
                dict_detalhes = {}
                for p in partes:
                    if ":" in p:
                        chave, valor = p.split(":", 1)
                        dict_detalhes[chave.strip()] = valor.strip()

                data_tela = formatar_data_vistoria_br(vist.get('data', 'N/A'))

                with col_info:
                    st.markdown(f"### 📦 {vist.get('item', 'Item')} — **Código:** `{vist.get('etiqueta', 'N/A')}`")
                    st.caption(f"📅 Data/Hora da Vistoria: {data_tela}")
                    
                    if "Estado" in dict_detalhes:
                        st.markdown(f"* **Estado:** {dict_detalhes['Estado']}")
                    if "Status" in dict_detalhes:
                        st.markdown(f"* **Status:** {dict_detalhes['Status']}")
                    if "Obs" in dict_detalhes:
                        st.markdown(f"* **Obs:** {dict_detalhes['Obs']}")
                    if "Auditor" in dict_detalhes:
                        st.markdown(f"* **Auditor:** {dict_detalhes['Auditor']}")

                with col_img:
                    foto = vist.get("foto") or vist.get("imagem")
                    if foto:
                        if isinstance(foto, str) and not foto.startswith("http"):
                            try:
                                foto = base64.b64decode(foto)
                            except Exception:
                                pass
                        
                        st.image(
                            foto,
                            caption=f"Foto da Vistoria ({vist.get('etiqueta', '')})",
                            use_container_width=True
                        )

                st.divider()
