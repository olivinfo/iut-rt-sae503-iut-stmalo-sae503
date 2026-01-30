import os, csv
from flask import Flask, request, jsonify
from redis import Redis
from flasgger import Swagger
from functools import wraps

app = Flask(__name__)
swagger = Swagger(app)

REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
ADMIN_KEY = os.getenv("ADMIN_KEY", "default_key")
CSV_FILE_USERS = "initial_data_users.csv"

redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

def authentification(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_key = request.headers.get("Authorization")
        if not auth_key or auth_key != ADMIN_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@app.avant_premiere_requete
def chargement_de_donnees():
    if not redis_client.exists("users"):
        if os.path.exists(CSV_FILE_USERS):
            with open(CSV_FILE_USERS, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    redis_client.hset(f"users:{row['id']}", mapping=row)
                    redis_client.sadd("users", f"users:{row['id']}")

@app.route('/users', methods=['GET'])
@authentification
def get_users():
    users = [redis_client.hgetall(uid) for uid in redis_client.smembers("users")]
    return jsonify(users), 200

@app.route('/users', methods=['POST'])
@authentification
def add_user():
    data = request.get_json()
    uid = data.get("id")
    if not uid: return jsonify({"error": "ID requis"}), 400
    redis_client.hset(f"users:{uid}", mapping=data)
    redis_client.sadd("users", f"users:{uid}")
    return jsonify({"message": "Utilisateur ajouté"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("APP_PORT", 5000)))
