"""
Docstring for citations_haddock.quotes.quotes
A Flask application to manage quotes with Redis as the database.
Provides endpoints to add and delete quotes with authentication.
"""

import os
import csv
from functools import wraps
from flask import Flask, request, jsonify
from redis import Redis
from flasgger import Swagger

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
APP_PORT = int(os.getenv("APP_PORT", "5000"))
ADMIN_KEY = os.getenv("ADMIN_KEY", "default_key")
CSV_FILE_QUOTES = os.getenv("CSV_FILE_QUOTES", "initial_data_quotes.csv")

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

if not redis_client.exists("quotes:1"):
    if os.path.exists(CSV_FILE_QUOTES):
        print("Citations trouvées")
        with open(CSV_FILE_QUOTES, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                quote=row['quote']
                quote_id = redis_client.incr("quote_id")
                redis_client.hset(f"quotes:{quote_id}", mapping={"quote": quote})
                redis_client.sadd("quotes", f"quotes:{quote_id}")
    else:
        print("/!\\ Pas de CSV trouver pour les citations /!\\")


# @app.route('/')
# def helloworld():

#     return jsonify({"message": "Hello World"}), 200

# Endpoint: Service des citations
@app.route('/quotes', methods=['GET'])
def get_quotes():
    """
    Récupérer toutes les citations
    ---
    security:
      - APIKeyAuth: []
    responses:
      200:
        description: Liste des citations
    """
    quotes = redis_client.smembers("quotes")
    quote_list=[]
    for quote in quotes: # type: ignore
        quote_list.append(redis_client.hgetall(quote))
    return jsonify(quote_list), 200

@app.route('/quotes', methods=['POST'])
@require_auth
def add_quote():
    data = request.get_json()
    user_id = data.get("user_id")
    quote = data.get("quote")

    if not user_id or not quote:
        return jsonify({"error": "user_id et quote sont requis"}), 400

    quote_id = redis_client.incr("quote_id")
    key = f"quotes:{quote_id}"
    redis_client.hset(key, mapping={"user_id": user_id, "quote": quote})
    redis_client.sadd("quotes", key)
    return jsonify({"message": "Citation ajoutée", "id": quote_id}), 201

@app.route('/quotes/<int:quote_id>', methods=['DELETE'])
@require_auth
def delete_quote(quote_id):
    key = f"quotes:{quote_id}"
    if not redis_client.hexists(key, "quote"):
        return jsonify({"error": "Citation non trouvée"}), 404

    redis_client.delete(key)
    redis_client.srem("quotes", key)
    return jsonify({"message": "Citation supprimée"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=APP_PORT)
