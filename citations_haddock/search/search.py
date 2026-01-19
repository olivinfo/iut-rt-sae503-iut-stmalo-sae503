import os
from flask import Flask, request, jsonify
from redis import Redis
from flasgger import Swagger
from functools import wraps

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
APP_PORT = int(os.getenv("APP_PORT", 5002))
ADMIN_KEY = os.getenv("ADMIN_KEY", "default_key")

app = Flask(__name__)
swagger = Swagger(app)
redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_key = request.headers.get("Authorization")
        if not auth_key or auth_key != ADMIN_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/search', methods=['GET'])
@require_auth
def search_quotes():
    keyword = request.args.get("keyword")
    if not keyword:
        return jsonify({"error": "Mot-clé requis"}), 400
    members = redis_client.smembers("quotes")
    filtered_quotes = []
    for member in members:
        quote_object = redis_client.hgetall(member)
        quote = quote_object.get("quote","")
        if keyword.lower() in quote.lower():
            filtered_quotes.append(quote)
    return jsonify(filtered_quotes), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=APP_PORT)
