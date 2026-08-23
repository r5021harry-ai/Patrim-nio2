import hashlib

def hash_password(password: str) -> str:
    """Gera um hash SHA-256 para a senha."""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(users_db: dict, username: str, password: str):
    """Autentica o usuário verificando o hash ou texto da senha com segurança."""
    if not users_db or username not in users_db:
        return False, None

    user = users_db.get(username)
    
    # Trata caso o valor armazenado seja uma string simples ou um dicionário
    if isinstance(user, str):
        stored_password = user
        role = "admin" if username == "admin" else "user"
    elif isinstance(user, dict):
        stored_password = user.get("password", "")
        role = user.get("role", "user")
    else:
        return False, None

    hashed_input = hash_password(password)
    
    # Comparação segura contra textos e hashes
    if stored_password and (stored_password == password or stored_password == hashed_input):
        return True, role

    return False, None

def create_user(users_db: dict, username: str, password: str, role: str = "user"):
    """Cria um novo usuário com senha criptografada."""
    if username in users_db:
        return False, "Usuário já existe!"
    
    users_db[username] = {
        "password": hash_password(password),
        "role": role
    }
    return True, "Usuário criado com sucesso!"

def update_password(users_db: dict, username: str, new_password: str):
    """Atualiza a senha do usuário existente."""
    if username in users_db:
        if isinstance(users_db[username], dict):
            users_db[username]["password"] = hash_password(new_password)
        else:
            users_db[username] = {
                "password": hash_password(new_password),
                "role": "admin" if username == "admin" else "user"
            }
        return True
    return False

def delete_user(users_db: dict, username: str):
    """Remove um usuário do banco de dados."""
    if username in users_db:
        del users_db[username]
        return True, "Usuário removido com sucesso!"
    return False, "Usuário não encontrado."
