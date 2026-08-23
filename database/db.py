import json
import os

ARQUIVO_DE_USUARIOS = "users.json"
PATRIMONIO_FILE = "patrimonio.json"
ARQUIVO_HISTORICO = "historico.json"

def load_json(caminho_do_arquivo, padrao):
    if os.path.exists(caminho_do_arquivo):
        try:
            with open(caminho_do_arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return padrao

def save_json(caminho_do_arquivo, dados):
    with open(caminho_do_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def obter_patrimonio_inicial():
    return []

def load_all_data():
    usuarios = load_json(ARQUIVO_DE_USUARIOS, {"admin": {"senha": "123", "papel": "admin"}})
    patrimonio = load_json(PATRIMONIO_FILE, obter_patrimonio_inicial())
    historico = load_json(ARQUIVO_HISTORICO, [])
    
    return usuarios, patrimonio, historico

# Alias de compatibilidade
cargar_json = load_json
salvar_json = save_json
cargar_todos_os_dados = load_all_data
