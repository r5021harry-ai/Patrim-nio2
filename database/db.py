import json
import os

# Arquivo JSON que funcionará como banco de dados local
DB_FILE = "dados_patrimonio.json"

def load_all_data():
    """Carrega os dados salvos do arquivo JSON."""
    if not os.path.exists(DB_FILE):
        return {}, [], [], []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return (
                data.get("users", {}),
                data.get("patrimonio", []),
                data.get("historico", []),
                data.get("cidades", [])
            )
    except Exception as e:
        print(f"Erro ao carregar banco de dados: {e}")
        return {}, [], [], []

def save_all_data(users, patrimonio, historico, cidades):
    """Grava imediatamente as alterações no arquivo JSON."""
    data = {
        "users": users,
        "patrimonio": patrimonio,
        "historico": historico,
        "cidades": cidades
    }
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao salvar no banco de dados: {e}")
        return False
