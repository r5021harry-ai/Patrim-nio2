import streamlit as st
import io
import os
from fpdf import FPDF
import barcode
from barcode.writer import ImageWriter

def gerar_codigo_barras(etiqueta_str):
    """Gera o buffer de imagem PNG do código de barras."""
    rv = io.BytesIO()
    code128 = barcode.get_barcode_class('code128')
    bc = code128(etiqueta_str, writer=ImageWriter())
    bc.write(rv, options={"module_height": 10.0, "font_size": 10, "text_distance": 3.0, "quiet_zone": 2.0})
    rv.seek(0)
    return rv

def gerar_pdf_etiqueta(item, logo_path="logo.png"):
    """Gera PDF de etiqueta individual tamanho padrão 50x30mm."""
    pdf = FPDF(orientation='L', unit='mm', format=(30, 50))
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    
    # Borda verde
    pdf.set_line_width(0.3)
    pdf.set_draw_color(0, 100, 50)
    pdf.rect(1, 1, 48, 28)

    # 1. LOGO OU TÍTULO NO TOPO
    if logo_path and os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=16, y=2.5, w=18)
            pdf.set_y(8.5)
        except Exception:
            pdf.set_font("Arial", "B", 8)
            pdf.set_text_color(0, 100, 50)
            pdf.cell(0, 4, "ISPN PATRIMÔNIO", 0, 1, 'C')
    else:
        pdf.set_font("Arial", "B", 8)
        pdf.set_text_color(0, 100, 50)
        pdf.cell(0, 4, "ISPN PATRIMÔNIO", 0, 1, 'C')

    # 2. NOME DO ITEM
    pdf.set_font("Arial", "B", 7)
    pdf.set_text_color(0, 0, 0)
    nome_bem = str(item.get('nome', 'N/A'))[:25]
    pdf.cell(0, 3.5, nome_bem, 0, 1, 'C')

    # 3. CÓDIGO DE BARRAS
    etiqueta = str(item.get('etiqueta', '00000'))
    bc_buffer = gerar_codigo_barras(etiqueta)
    
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        tmp.write(bc_buffer.getvalue())
        tmp_path = tmp.name

    pdf.image(tmp_path, x=6, y=12, w=38, h=15)
    
    try:
        os.remove(tmp_path)
    except Exception:
        pass

    return bytes(pdf.output(dest='S'))

def render_etiquetas(patrimonio_db, logo_path="logo.png"):
    """Exibe a interface de geração e impressão de etiquetas."""
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

            # --- PREVISÃO DA ETIQUETA ---
            with col_card:
                bc_buffer = gerar_codigo_barras(str(item.get('etiqueta', '00000')))
                
                with st.container(border=True):
                    if os.path.exists(logo_path):
                        col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
                        with col_l2:
                            st.image(logo_path, use_container_width=True)
                    else:
                        st.markdown("<h4 style='text-align: center; color: #006432; margin: 0;'>ISPN PATRIMÔNIO</h4>", unsafe_allow_html=True)

                    st.markdown(f"<p style='text-align: center; font-weight: bold; margin: 5px 0;'>{item.get('nome', '')}</p>", unsafe_allow_html=True)
                    st.image(bc_buffer, use_container_width=True)

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
                nf_arq = item.get('arquivo_nf') or "Nenhum arquivo anexado"

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
    """Função principal chamada pelo app.py para renderizar a página de relatórios/etiquetas."""
    st.title("Relatórios e Etiquetas")
    render_etiquetas(patrimonio_db)
