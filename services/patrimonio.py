import io
import os
import tempfile
from datetime import datetime
from database.db import save_json, PATRIMONIO_FILE, HISTORICO_FILE

# Importações para geração do PDF e QR Code
from fpdf import FPDF
import qrcode

# Caminho absoluto para encontrar a imagem logo.png na pasta raiz
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGO_PATH_DEFAULT = os.path.join(BASE_DIR, "logo.png")


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


def gerar_pdf_etiqueta(item, logo_path=None):
    """
    Gera PDF de etiqueta individual (50x30mm) fiel ao modelo da foto:
    - Esquerda: Logo completa (logo.png)
    - Direita: Texto 'Patrimônio', QR Code e o Número do Código
    """
    if logo_path is None:
        logo_path = LOGO_PATH_DEFAULT

    pdf = FPDF(orientation='L', unit='mm', format=(30, 50))
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    
    # Borda fina e arredondada/discreta ao redor da etiqueta
    pdf.set_line_width(0.2)
    pdf.set_draw_color(200, 200, 200)
    pdf.rect(1, 1, 48, 28)

    # 1. ESQUERDA: LOGO COMPLETA (logo.png)
    if os.path.exists(logo_path):
        try:
            # Insere a logo.png alinhada à esquerda
            pdf.image(logo_path, x=3, y=4, w=22)
        except Exception:
            pass

    # 2. DIREITA: ETIQUETA E QR CODE
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

    # Insere o QR Code centralizado no lado direito
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


def add_patrimonio(patrimonio_db, historico_db, etiqueta, nome, categoria, localizacao, status, responsavel):
    etiqueta = etiqueta.strip().upper()
    if any(item["etiqueta"] == etiqueta for item in patrimonio_db):
        return False, "Já existe um item com essa etiqueta!"
    
    novo_item = {
        "etiqueta": etiqueta,
        "nome": nome.strip(),
        "categoria": categoria,
        "localizacao": localizacao,
        "status": status,
        "responsavel": responsavel.strip()
    }
    patrimonio_db.append(novo_item)
    historico_db.append({
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "etiqueta": etiqueta,
        "item": nome.strip(),
        "acao": "Cadastro Novo",
        "responsavel": responsavel.strip(),
        "localizacao": localizacao
    })
    save_json(PATRIMONIO_FILE, patrimonio_db)
    save_json(HISTORICO_FILE, historico_db)
    return True, f"Item '{nome}' cadastrado com sucesso!"


def update_patrimonio(patrimonio_db, etiqueta, nome, categoria, localizacao, status, responsavel):
    for item in patrimonio_db:
        if item["etiqueta"] == etiqueta:
            item["nome"] = nome
            item["categoria"] = categoria
            item["localizacao"] = localizacao
            item["status"] = status
            item["responsavel"] = responsavel
            save_json(PATRIMONIO_FILE, patrimonio_db)
            return True, "Dados atualizados!"
    return False, "Item não encontrado."


def delete_patrimonio(patrimonio_db, historico_db, etiqueta):
    etiqueta = etiqueta.strip().upper()
    for index, item in enumerate(patrimonio_db):
        if item["etiqueta"] == etiqueta:
            item_removido = patrimonio_db.pop(index)
            historico_db.append({
                "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "etiqueta": etiqueta,
                "item": item_removido["nome"],
                "acao": "Exclusão",
                "responsavel": item_removido.get("responsavel", "Admin"),
                "localizacao": item_removido.get("localizacao", "")
            })
            save_json(PATRIMONIO_FILE, patrimonio_db)
            save_json(HISTORICO_FILE, historico_db)
            return True, f"Patrimônio '{etiqueta}' excluído com sucesso!"
    return False, "Item não encontrado."
