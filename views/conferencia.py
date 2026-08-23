import streamlit as st
import pandas as pd
from datetime import datetime
import importlib
import base64

# Tenta importar bibliotecas de leitura de código de barras
try:
    from PIL import Image
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
        img = Image.open(image_file)
        decoded_objs = decode_barcode(img)
        for obj in decoded_objs:
            return obj.data.decode("utf-8").strip()
    except Exception:
        pass
    return None

def render_conferencia(patrimonio_db, historico_db, cidades_db=None):
    st.title("📱 Conferência e Auditoria de Patrimônio")
    st.caption("Faça a verificação de inventário escaneando a etiqueta ou digitando o código do bem.")

    if not patrimonio_db:
        st.warning("Nenhum patrimônio cadastrado no sistema.")
        return

    df = pd.DataFrame(patrimonio_db)
    
    # Mapeamento dinâmico e seguro de colunas
    col_etiqueta = 'patrimonio' if 'patrimonio' in df.columns else ('etiqueta' if 'etiqueta' in df.columns else df.columns[0])
    col_nome = 'descricao' if 'descricao' in df.columns else ('nome' if 'nome' in df.columns else ('item' if 'item' in df.columns else df.columns[1]))
    col_status = 'estado' if 'estado' in df.columns else ('status' if 'status' in df.columns else df.columns[2])
    col_local = 'cidade' if 'cidade' in df.columns else ('localizacao' if 'localizacao' in df.columns else df.columns[3])
    col_responsavel = 'usuario' if 'usuario' in df.columns else ('responsavel' if 'responsavel' in df.columns else df.columns[4])

    if "msg_conf_sucesso" in st.session_state:
        st.success(st.session_state.msg_conf_sucesso)
        del st.session_state.msg_conf_sucesso

    # --- SELEÇÃO DO MÉTODO DE ENTRADA ---
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

    # --- PROCESSAMENTO DO ITEM ENCONTRADO ---
    if codigo_buscado:
        idx = next((i for i, item in enumerate(patrimonio_db) if str(item.get(col_etiqueta, '')).upper() == codigo_buscado.upper()), None)
        
        if idx is None:
            st.error(f"Patrimônio com código **{codigo_buscado}** não foi encontrado no sistema.")
        else:
            item = patrimonio_db[idx]
            st.divider()
            
            # Exibição dos Dados do Item Encontrado
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
                
                # Escolha de método para anexar a foto
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
                    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    usuario_auditor = st.session_state.get('username', 'usuario')

                    # Prepara registro de vistoria
                    patrimonio_db[idx][col_status] = novo_status
                    patrimonio_db[idx]['ultimo_estado'] = estado_conservacao
                    patrimonio_db[idx]['ultima_vistoria'] = data_hora
                    patrimonio_db[idx]['vistoriado_por'] = usuario_auditor

                    # Converte imagem para Base64 se enviada
                    foto_b64 = ""
                    if foto_vistoria is not None:
                        foto_bytes = foto_vistoria.getvalue()
                        foto_b64 = base64.b64encode(foto_bytes).decode('utf-8')

                    # Adiciona no histórico
                    historico_db.append({
                        "data": data_hora,
                        "etiqueta": item.get(col_etiqueta),
                        "item": item.get(col_nome),
                        "acao": "Auditoria / Vistoria",
                        "detalhes": f"Estado: {estado_conservacao} | Status: {novo_status} | Obs: {obs} | Auditor: {usuario_auditor}",
                        "foto": foto_b64
                    })

                    # Salva no banco de dados
                    if save_all_data:
                        users_db = st.session_state.get('users_db', {})
                        cidades = st.session_state.get('cidades_db', {})
                        save_all_data(users_db, patrimonio_db, historico_db, cidades)

                    st.session_state.msg_conf_sucesso = f"Conferência do item {item.get(col_etiqueta)} registrada com sucesso por {usuario_auditor}!"
                    st.rerun()

    # --- PAINEL DE VISTORIAS REALIZADAS ---
    st.divider()
    st.subheader("📸 Painel Exclusivo de Vistorias Realizadas")

    # Filtra histórico por ações de Vistoria/Auditoria
    vistorias = [h for h in historico_db if "Vistoria" in h.get("acao", "") or "Auditoria" in h.get("acao", "")]

    if not vistorias:
        st.info("Nenhuma vistoria ou auditoria registrada até o momento.")
    else:
        # Filtro opcional por item no histórico
        opcoes_filtro = ["-- Exibir Todos --"] + sorted(list(set(f"{h.get('etiqueta')} - {h.get('item')}" for h in vistorias if h.get('etiqueta'))))
        filtro_sel = st.selectbox("Filtrar por Código de Patrimônio:", opcoes_filtro)

        if filtro_sel != "-- Exibir Todos --":
            cod_filtro = filtro_sel.split(" - ")[0]
            vistorias = [h for h in vistorias if str(h.get("etiqueta")) == cod_filtro]

        # Exibe em ordem decrescente (mais recentes primeiro)
        for vist in reversed(vistorias):
            with st.container():
                # Colunas [3, 1] mantêm texto próximo e foto compacta no lado direito
                col_info, col_img = st.columns([3, 1])

                # Processamento das informações do texto
                detalhes = vist.get("detalhes", "")
                partes = [p.strip() for p in detalhes.split("|")]
                
                dict_detalhes = {}
                for p in partes:
                    if ":" in p:
                        chave, valor = p.split(":", 1)
                        dict_detalhes[chave.strip()] = valor.strip()

                with col_info:
                    st.markdown(f"### 📦 {vist.get('item', 'Item')} — **Código:** `{vist.get('etiqueta', 'N/A')}`")
                    st.caption(f"📅 Data/Hora: {vist.get('data', 'N/A')}")
                    
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
                        # Se estiver em Base64, decodifica
                        if isinstance(foto, str) and not foto.startswith("http"):
                            try:
                                foto = base64.b64decode(foto)
                            except Exception:
                                pass
                        
                        # Limita a largura em 220px para aprox. e manter o layout compacto
                        st.image(
                            foto,
                            caption=f"Foto da Vistoria ({vist.get('etiqueta', '')})",
                            width=220
                        )

                st.divider()
