import json
import os

USERS_FILE = "users.json"
PATRIMONIO_FILE = "patrimonio.json"
HISTORICO_FILE = "historico.json"

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_initial_patrimonio():
    return [
        {"etiqueta": "PAT-001", "nome": "Notebook Lenovo ThinkPad", "categoria": "Informática", "localizacao": "Campo - Cerrado", "status": "Em Uso", "responsavel": "Celso (Técnico)"},
        {"etiqueta": "PAT-002", "nome": "Toyota Hilux 4x4", "categoria": "Veículo", "localizacao": "Campo - Cerrado", "status": "Em Uso", "responsavel": "Equipe de Campo"},
        {"etiqueta": "PAT-003", "nome": "Mesa de Escritório Madeira", "categoria": "Móveis", "localizacao": "Sede DF", "status": "Disponível", "responsavel": "Nenhum"},
        {"etiqueta": "PAT-004", "nome": "Ar Condicionado Split 12000 BTU", "categoria": "Eletrodomésticos", "localizacao": "Almoxarifado", "status": "Em Manutenção", "responsavel": "Manutenção Técnica"},
        {"etiqueta": "PAT-005", "nome": "Prédio Sede ISPN", "categoria": "Imóvel", "localizacao": "Sede DF", "status": "Em Uso", "responsavel": "Administrativo ISPN"}
    ]

def load_all_data():
    users = load_json(USERS_FILE, {"admin": {"password": "1234", "role": "admin"}})
    patrimonio = load_json(PATRIMONIO_FILE, get_initial_patrimonio())
    historico = load_json(HISTORICO_FILE, [
        {"data": "2026-08-20 10:00", "etiqueta": "PAT-001", "item": "Notebook Lenovo ThinkPad", "acao": "Saída", "responsavel": "Celso (Técnico)", "localizacao": "Campo - Cerrado"}
    ])
    return users, patrimonio, historico
