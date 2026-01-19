import os
import csv
from flask import Flask, request, jsonify
from redis import Redis
from flasgger import Swagger
from functools import wraps

# Configuration des variables d'environnement
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
APP_PORT = int(os.getenv("APP_PORT", 5000))
ADMIN_KEY = os.getenv("ADMIN_KEY", "default_key")
CSV_FILE_USERS = os.getenv("CSV_FILE_USERS", "initial_data_users.csv")

app = Flask(__name__)
swagger = Swagger(app)

redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_key = request.headers.get("Authorization")
        if not auth_key or auth_key != ADMIN_KEY:
            return jsonify({"error": "Unauthorized"}), 401
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

@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({"message": "User Service Online"})

@app.route('/users', methods=['GET'])
@require_auth
def get_users():
    users_ids = redis_client.smembers("users")
    users = [redis_client.hgetall(user_id) for user_id in users_ids]
    return jsonify(users), 200

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
