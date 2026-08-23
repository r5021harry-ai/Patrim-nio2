from database.db import save_json, PATRIMONIO_FILE, HISTORICO_FILE
from datetime import datetime

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
