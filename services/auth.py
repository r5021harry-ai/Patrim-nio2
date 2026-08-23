from database.db import save_json, USERS_FILE

def authenticate_user(users_db, username, password):
    if username in users_db and users_db[username]["password"] == password:
        return True, users_db[username]["role"]
    return False, None

def create_user(users_db, username, password, role):
    if username in users_db:
        return False, "Usuário já existe."
    users_db[username] = {"password": password, "role": role}
    save_json(USERS_FILE, users_db)
    return True, f"Usuário '{username}' criado com sucesso!"

def update_password(users_db, username, new_password):
    users_db[username]["password"] = new_password
    save_json(USERS_FILE, users_db)
    return True, "Senha alterada com sucesso!"
