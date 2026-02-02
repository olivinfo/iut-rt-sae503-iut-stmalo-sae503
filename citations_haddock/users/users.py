import os
import csv
from functools import wraps
import json
import secrets
from flask import Flask, request, jsonify
from redis import Redis
from flasgger import Swagger

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
APP_PORT = int(os.getenv("APP_PORT", "5000"))
ADMIN_KEY = json.loads(os.getenv("ADMIN_KEY", '["default_key"]'))
CSV_FILE_USERS = os.getenv("CSV_FILE_USERS", "initial_data_users.csv")

app = Flask(__name__)
swagger = Swagger(app)

redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Récupère la clé d'authentification depuis l'en-tête Authorization
        auth_key = request.headers.get("Authorization")

        # Vérifie si la clé est présente
        if not auth_key:
            return jsonify({"error": "Authorization header is missing"}), 401

        # Construit la clé Redis pour le token
        token_key = f"token:{auth_key}"

        # Vérifie si le token existe dans Redis
        if not redis_client.exists(token_key):
            return jsonify({"error": "Unauthorized: Invalid token"}), 401

        # Optionnel : Vérifie si le token a des informations valides
        token_data = redis_client.hgetall(token_key)
        if not token_data:
            return jsonify({"error": "Unauthorized: Token data is invalid"}), 401

        # Si tout est valide, exécute la fonction décorée
        return f(*args, **kwargs)
    return decorated


# Chargement initial des données utilisateurs
if not redis_client.exists("users"):
    if os.path.exists(CSV_FILE_USERS):
        with open(CSV_FILE_USERS, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                uid, name, password = row['id'], row['name'], row['password']
                redis_client.hset(f"users:{uid}", mapping={"id": uid,"name": name, "password": password})
                redis_client.sadd("users", f"users:{uid}")

# Créé la table des token utilisateurs
if not redis_client.exists("token"):
    for uuid in ADMIN_KEY:
        # Ajoute un hash pour chaque utilisateur
        redis_client.hset(
            f"token:{uuid}",
            mapping={
                "id": uuid,
                "name": "admin",
            }
        )
        # Ajoute la clé du hash au set "token"
        redis_client.sadd("token", f"token:{uuid}")



@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({"message": "User Service Online"})

@app.route('/users/health')
def helloworld():

    return jsonify({"message": "healthy"}), 200

@app.route('/users', methods=['GET'])
@require_auth
def get_users():
    users_ids = redis_client.smembers("users")
    users = [redis_client.hgetall(user_id) for user_id in users_ids] # type: ignore
    return jsonify(users), 200

@app.route('/users/all', methods=['GET'])
def get_all_users():
    # Récupère toutes les clés des utilisateurs depuis le set "users"
    user_keys = redis_client.smembers("users")
    # Pour chaque clé, récupère les informations de l'utilisateur
    users = []
    for key in user_keys: # type: ignore
        user_data = redis_client.hgetall(key)
        users.append(user_data)
    return jsonify(users), 200

@app.route('/users/token', methods=['GET'])
def get_all_tokens():
    # Récupère toutes les clés des utilisateurs depuis le set "users"
    user_keys = redis_client.smembers("token")
    # Pour chaque clé, récupère les informations de l'utilisateur
    users = []
    for key in user_keys: # type: ignore
        user_data = redis_client.hgetall(key)
        users.append(user_data)
    return jsonify(users), 200

@app.route('/users/login', methods=['POST'])
def login_user():
    data = request.get_json()
    name = data.get("name")
    password = data.get("password")

    if not name or not password:
        return jsonify({"error": "Nom et mot de passe sont requis"}), 400

    user_keys = redis_client.smembers("users")
    for user_key in user_keys:
        user_data = redis_client.hgetall(user_key)
        if user_data.get("name") == name and user_data.get("password") == password:
            token = secrets.token_hex(16)

            redis_client.hset(
                f"token:{token}",
                mapping={
                    "id": user_data.get("id"),
                    "name": user_data.get("name"),
                }
            )
            redis_client.sadd("token", f"token:{token}")

            return jsonify({
                "token": token,
                "user_id": user_data.get("id")
            }), 200

    return jsonify({"error": "Nom d'utilisateur ou mot de passe incorrect"}), 401


@app.route('/users', methods=['POST'])
@require_auth
def add_user():
    data = request.get_json()
    user_id, name, password = data.get("id"), data.get("name"), data.get("password")
    if not user_id or not name:
        return jsonify({"error": "ID et nom sont requis"}), 400
    redis_client.hset(f"users:{user_id}", mapping={"id": user_id,"name": name, "password": password})
    redis_client.sadd("users", f"users:{user_id}")
    return jsonify({"message": "Utilisateur ajouté"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=APP_PORT)
