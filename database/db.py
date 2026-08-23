import json
import os

USERS_FILE = "users.json"
PATRIMONIO_FILE = "patrimonio.json"
HISTORICO_FILE = "historico.json"

def load_json(caminho, padrao):
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return padrao

def save_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def load_all_data():
    usuarios = load_json(USERS_FILE, {"admin": {"senha": "123", "papel": "admin"}})
    patrimonio = load_json(PATRIMONIO_FILE, [])
    historico = load_json(HISTORICO_FILE, [])
    return usuarios, patrimonio, historico
