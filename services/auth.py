import hashlib

def hash_password(password: str) -> str:
    """Gera um hash SHA-256 para a senha."""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(users_db: dict, username: str, password: str):
    """Autentica o usuário verificando o hash da senha."""
    user = users_db.get(username)
    if not user:
        return False, None
    
    # Suporta senhas antigas em texto puro e senhas em Hash
    hashed_input = hash_password(password)
    if user["password"] == password or user["password"] == hashed_input:
        return True, user.get("role", "user")
    
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
        users_db[username]["password"] = hash_password(new_password)
        return True
    return False

def delete_user(users_db: dict, username: str):
    """Remove um usuário do banco de dados."""
    if username in users_db:
        del users_db[username]
        return True, "Usuário removido com sucesso!"
    return False, "Usuário não encontrado."
