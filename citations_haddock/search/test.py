from unittest.mock import patch
import pytest
from search import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_search_no_keyword(client):
    """Teste l'erreur si le mot-clé est absent"""
    response = client.get('/search', headers={'Authorization': 'default_key'})
    assert response.status_code == 400
    assert response.json == {"error": "Mot-clé requis"}

def test_search_unauthorized(client):
    """Teste le refus d'accès sans clé API"""
    response = client.get('/search?keyword=test')
    assert response.status_code == 401
    assert response.json == {'error': 'Authorization header is missing'}

def test_search_quotes_success(client):
    """Teste une recherche réussie avec Mock de Redis"""
    with patch('search.redis_client') as mock_redis:
        # Simulation des données dans Redis
        mock_redis.smembers.return_value = {"quotes:1", "quotes:2"}

        # Utilisation d'une fonction pour side_effect
        def hgetall_side_effect(key):
            if key == "quotes:1":
                return {"quote": "Mille sabords !"}
            if key == "quotes:2":
                return {"quote": "Tonnerre de Brest !"}
            return {}

        mock_redis.hgetall.side_effect = hgetall_side_effect

        response = client.get('/search?keyword=Brest', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert b"Tonnerre de Brest !" in response.data

def test_search_quotes_no_results(client):
    """Teste une recherche qui ne trouve rien"""
    with patch('search.redis_client') as mock_redis:
        mock_redis.smembers.return_value = {"quotes:1"}
        mock_redis.hgetall.return_value = {"quote": "Mille sabords !"}

        response = client.get('/search?keyword=Inconnu', headers={'Authorization': 'default_key'})

        assert response.status_code == 200
        assert response.json == []

def test_search_with_alice_auth(client):
    """Teste la recherche avec la clé d'Alice (devrait échouer)"""
    response = client.get('/search?keyword=test', headers={'Authorization': 'inWonderland'})
    assert response.status_code == 401
    assert response.json == {'error': 'Unauthorized: Invalid token'}

def test_search_case_insensitive(client):
    """Teste que la recherche est insensible à la casse"""
    with patch('search.redis_client') as mock_redis:
        mock_redis.smembers.return_value = {"quotes:1"}
        mock_redis.hgetall.return_value = {"quote": "Test de citation"}

        # Recherche en majuscules
        response = client.get('/search?keyword=TEST', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0] == "Test de citation"

def test_search_empty_keyword(client):
    """Teste la recherche avec un mot-clé vide"""
    response = client.get('/search?keyword=', headers={'Authorization': 'default_key'})
    assert response.status_code == 400
    assert response.json == {"error": "Mot-clé requis"}

def test_search_with_special_characters(client):
    """Teste la recherche avec des caractères spéciaux"""
    with patch('search.redis_client') as mock_redis:
        mock_redis.smembers.return_value = {"quotes:1"}
        mock_redis.hgetall.return_value = {"quote": "Citation avec émojis 😀"}

        response = client.get('/search?keyword=émojis', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 1

def test_search_multiple_matches(client):
    """Teste la recherche avec plusieurs correspondances"""
    with patch('search.redis_client') as mock_redis:
        mock_redis.smembers.return_value = {"quotes:1", "quotes:2", "quotes:3"}
        mock_redis.hgetall.side_effect = [
            {"quote": "Premier test de citation"},
            {"quote": "Deuxième citation de test"},
            {"quote": "Citation sans rapport"}
        ]

        response = client.get('/search?keyword=test', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 2
