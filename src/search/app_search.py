import os
from flask import Flask, request, jsonify
from redis import Redis
from flasgger import Swagger
from functools import wraps

app = Flask(__name__)
swagger = Swagger(app)

REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
ADMIN_KEY = os.getenv("ADMIN_KEY", "default_key")

redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

def authentification(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_key = request.headers.get("Authorization")
        if not auth_key or auth_key != ADMIN_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/search', methods=['GET'])
@authentification
def search_quotes():
    keyword = request.args.get("keyword", "").lower()
    if not keyword: return jsonify({"error": "Mot-clé requis"}), 400
    results = []
    for qid in redis_client.smembers("quotes"):
        quote = redis_client.hget(qid, "quote")
        if quote and keyword in quote.lower():
            results.append(quote)
    return jsonify(results), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("APP_PORT", 5000)))
