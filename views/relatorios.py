import streamlit as st
import io
import os
import tempfile
from fpdf import FPDF
import qrcode

# Caminho absoluto para encontrar a imagem logo.png na raiz do projeto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGO_PATH_DEFAULT = os.path.join(BASE_DIR, "logo.png")

def gerar_qrcode(conteudo_str):
    """Gera o buffer de imagem PNG do QR Code."""
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

def gerar_pdf_etiqueta(item, logo_path=None):
    """Gera PDF de etiqueta (50x30mm) fiel ao modelo físico (Logo na esquerda | QR Code e Patrimônio na direita)."""
    if logo_path is None:
        logo_path = LOGO_PATH_DEFAULT

    pdf = FPDF(orientation='L', unit='mm', format=(30, 50))
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    
    # Borda fina e discreta
    pdf.set_line_width(0.2)
    pdf.set_draw_color(200, 200, 200)
    pdf.rect(1, 1, 48, 28)

    # 1. COLUNA DA ESQUERDA: LOGO COMPLETA
    if os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=3, y=4, w=22)
        except Exception:
            pass

    # 2. COLUNA DA DIREITA: ETIQUETA E QR CODE
    # Texto "Patrimônio"
    pdf.set_xy(26, 3)
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(70, 70, 70)
    pdf.cell(21, 4, "Patrimônio", 0, 1, 'C')

    # QR Code
    etiqueta = str(item.get('etiqueta', '00000'))
    qr_buffer = gerar_qrcode(etiqueta)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        tmp.write(qr_buffer.getvalue())
        tmp_path = tmp.name

    pdf.image(tmp_path, x=29.5, y=7.5, w=14, h=14)

    # Número da Etiqueta
    pdf.set_xy(26, 22)
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(21, 4, etiqueta, 0, 1, 'C')
    
    try:
        os.remove(tmp_path)
    except Exception:
        pass

    return bytes(pdf.output(dest='S'))

def render_etiquetas(patrimonio_db, logo_path=None):
    """Exibe a interface de geração e impressão de etiquetas."""
    if logo_path is None:
        logo_path = LOGO_PATH_DEFAULT

    if not patrimonio_db:
        st.info("Nenhum patrimônio cadastrado para geração de etiqueta.")
        return

    opcoes = [f"{item.get('etiqueta', '')} - {item.get('nome', '')}" for item in patrimonio_db]
    sel_item_str = st.selectbox("Selecione o Patrimônio:", opcoes, key="relatorios_sel_patrimonio_unique")

    if sel_item_str:
        etiqueta_sel = sel_item_str.split(" - ")[0].strip()
        item = next((i for i in patrimonio_db if str(i.get("etiqueta")).strip() == etiqueta_sel), None)

        if item:
            col_card, col_detalhes = st.columns([1, 1])

            # --- PREVISÃO DA ETIQUETA NA TELA ---
            with col_card:
                qr_buffer = gerar_qrcode(str(item.get('etiqueta', '00000')))
                
                with st.container(border=True):
                    # Layout em 2 Colunas igual ao modelo da foto
                    col_logo, col_qr = st.columns([1.1, 1])

                    with col_logo:
                        if os.path.exists(logo_path):
                            st.image(logo_path, use_container_width=True)

                    with col_qr:
                        st.markdown("<p style='text-align: center; color: #444; margin: 0; font-size: 14px;'>Patrimônio</p>", unsafe_allow_html=True)
                        st.image(qr_buffer, use_container_width=True)
                        st.markdown(f"<p style='text-align: center; font-weight: bold; margin: 0; font-size: 14px;'>{item.get('etiqueta', '')}</p>", unsafe_allow_html=True)

                pdf_bytes = gerar_pdf_etiqueta(item, logo_path=logo_path)
                st.download_button(
                    label="Baixar Etiqueta em PDF (50x30mm)",
                    data=pdf_bytes,
                    file_name=f"etiqueta_{item.get('etiqueta')}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                    key="btn_download_etiqueta_pdf_unique"
                )

            # --- DETALHES FORMATADOS AO LADO ---
            with col_detalhes:
                val_num = item.get("valor_unitario", item.get("valor", 0.0))
                try:
                    val_float = float(val_num) if val_num is not None else 0.0
                except ValueError:
                    val_float = 0.0

                val_fmt = f"R$ {val_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                
                # --- TRATAMENTO CORRIGIDO PARA O ARQUIVO NF ---
                raw_nf = item.get('arquivo_nf')
                if isinstance(raw_nf, dict):
                    nf_arq = raw_nf.get("nome_arquivo", "Anexado")
                elif isinstance(raw_nf, str) and raw_nf.strip():
                    nf_arq = raw_nf
                else:
                    nf_arq = "Nenhum arquivo anexado"

                st.markdown(f"""
                **Código:** `{item.get('etiqueta', 'N/A')}`  
                **Item:** {item.get('nome', 'N/A')}  
                **Categoria:** {item.get('categoria', 'N/A')}  
                **Setor:** {item.get('setor', 'N/A')}  
                **Número NF:** {item.get('numero_nf', 'N/A')}  
                **Fornecedor:** {item.get('fornecedor', 'N/A')}  
                **Valor Unitário:** {val_fmt}  
                **Arquivo NF:** {nf_arq}  
                **Localização:** {item.get('localizacao', 'N/A')}  
                **Responsável:** {item.get('responsavel', 'N/A')}  
                **Estado:** {item.get('estado', 'N/A')}  
                **Placa:** {item.get('placa') or 'N/A'}  
                **Observações:** {item.get('observacoes') or 'Sem observações'}
                """)

def render_relatorios(patrimonio_db, *args, **kwargs):
    """Função principal chamada para renderizar a página de relatorios/etiquetas."""
    st.title("Relatórios e Etiquetas")
    render_etiquetas(patrimonio_db)
