from banco_dados.db import save_json, USERS_FILE

def authenticate_user(users_db, username, password):
    if username in users_db:
        user_data = users_db[username]
        pwd = user_data.get("senha") or user_data.get("password")
        role = user_data.get("papel") or user_data.get("role", "user")
        if str(pwd) == str(password):
            return True, role
    return False, None

def create_user(users_db, username, password, role):
    if username in users_db:
        return False, "Usuário já existe."
    users_db[username] = {"senha": password, "papel": role}
    save_json(USERS_FILE, users_db)
    return True, f"Usuário '{username}' criado com sucesso!"

def update_password(users_db, username, new_password):
    if username in users_db:
        if isinstance(users_db[username], dict):
            users_db[username]["senha"] = new_password
        save_json(USERS_FILE, users_db)
        return True, "Senha atualizada!"
    return False, "Usuário não encontrado."
