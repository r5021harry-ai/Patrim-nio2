import json
import os

ARQUIVO_DE_USUARIOS = "users.json"
PATRIMONIO_FILE = "patrimonio.json"
ARQUIVO_HISTORICO = "historico.json"

def cargar_json(caminho_do_arquivo, padrao):
    if os.path.exists(caminho_do_arquivo):
        try:
            with open(caminho_do_arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return padrao

def salvar_json(caminho_do_arquivo, dados):
    with open(caminho_do_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def obter_patrimonio_inicial():
    # Retorna uma lista vazia sem nenhum item de teste
    return []

def cargar_todos_os_dados():
    usuarios = cargar_json(ARQUIVO_DE_USUARIOS, {"admin": {"senha": "123", "papel": "admin"}})
    patrimonio = cargar_json(PATRIMONIO_FILE, obter_patrimonio_inicial())
    historico = cargar_json(ARQUIVO_HISTORICO, [])
    
    return usuarios, patrimonio, historico
