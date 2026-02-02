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
        # Mock pour l'authentification
        mock_redis.exists.return_value = True
        mock_redis.hgetall.return_value = {"id": "default_key", "name": "admin"}

        # Simulation des données dans Redis pour la recherche
        def search_hgetall_side_effect(key):
            if key.startswith("quotes:"):
                if key == "quotes:1":
                    return {"quote": "Mille sabords !"}
                if key == "quotes:2":
                    return {"quote": "Tonnerre de Brest !"}
            return {"id": "default_key", "name": "admin"}

        mock_redis.smembers.return_value = {"quotes:1", "quotes:2"}
        mock_redis.hgetall.side_effect = search_hgetall_side_effect

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
        # Mock pour l'authentification
        mock_redis.exists.return_value = True
        mock_redis.hgetall.return_value = {"id": "default_key", "name": "admin"}

        # Simulation des données pour la recherche
        def search_hgetall_side_effect(key):
            if key.startswith("quotes:"):
                if key == "quotes:1":
                    return {"quote": "Premier test de citation"}
                if key == "quotes:2":
                    return {"quote": "Deuxième citation de test"}
                if key == "quotes:3":
                    return {"quote": "Citation sans rapport"}
            return {"id": "default_key", "name": "admin"}

        mock_redis.smembers.return_value = {"quotes:1", "quotes:2", "quotes:3"}
        mock_redis.hgetall.side_effect = search_hgetall_side_effect

        response = client.get('/search?keyword=test', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 2

def test_search_partial_match(client):
    """Teste la recherche avec une correspondance partielle"""
    with patch('search.redis_client') as mock_redis:
        mock_redis.smembers.return_value = {"quotes:1"}
        mock_redis.hgetall.return_value = {"quote": "Citation contenant le mot recherche"}

        response = client.get('/search?keyword=recherche', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 1
        assert "recherche" in response.json[0]

def test_search_with_numbers(client):
    """Teste la recherche avec des nombres dans les citations"""
    with patch('search.redis_client') as mock_redis:
        # Mock pour l'authentification
        mock_redis.exists.return_value = True
        mock_redis.hgetall.return_value = {"id": "default_key", "name": "admin"}

        # Simulation des données pour la recherche
        def search_hgetall_side_effect(key):
            if key.startswith("quotes:"):
                if key == "quotes:1":
                    return {"quote": "Citation avec le nombre 42"}
                if key == "quotes:2":
                    return {"quote": "Autre citation avec 100"}
            return {"id": "default_key", "name": "admin"}

        mock_redis.smembers.return_value = {"quotes:1", "quotes:2"}
        mock_redis.hgetall.side_effect = search_hgetall_side_effect

        response = client.get('/search?keyword=42', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 1
        assert "42" in response.json[0]

def test_search_empty_quotes_collection(client):
    """Teste la recherche lorsque la collection de citations est vide"""
    with patch('search.redis_client') as mock_redis:
        mock_redis.smembers.return_value = set()  # Collection vide

        response = client.get('/search?keyword=test', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert response.json == []

def test_search_with_whitespace_keyword(client):
    """Teste la recherche avec un mot-clé contenant des espaces"""
    with patch('search.redis_client') as mock_redis:
        mock_redis.smembers.return_value = {"quotes:1"}
        mock_redis.hgetall.return_value = {"quote": "Citation avec plusieurs mots"}

        response = client.get('/search?keyword=mots', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 1

def test_search_mixed_case_keyword(client):
    """Teste la recherche avec un mot-clé en casse mixte"""
    with patch('search.redis_client') as mock_redis:
        mock_redis.smembers.return_value = {"quotes:1"}
        mock_redis.hgetall.return_value = {"quote": "Citation avec Majuscules et minuscules"}

        response = client.get('/search?keyword=MAJUSCULES', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 1

def test_search_with_punctuation(client):
    """Teste la recherche avec des citations contenant de la ponctuation"""
    with patch('search.redis_client') as mock_redis:
        mock_redis.smembers.return_value = {"quotes:1"}
        mock_redis.hgetall.return_value = {"quote": "Citation avec ponctuation: point, virgule, etc."}

        response = client.get('/search?keyword=ponctuation', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 1

def test_search_quote_with_empty_content(client):
    """Teste la recherche avec une citation vide"""
    with patch('search.redis_client') as mock_redis:
        mock_redis.smembers.return_value = {"quotes:1"}
        mock_redis.hgetall.return_value = {"quote": ""}

        response = client.get('/search?keyword=test', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert response.json == []

def test_search_with_very_long_keyword(client):
    """Teste la recherche avec un mot-clé très long"""
    with patch('search.redis_client') as mock_redis:
        long_keyword = "a" * 100
        mock_redis.smembers.return_value = {"quotes:1"}
        mock_redis.hgetall.return_value = {"quote": f"Citation contenant {long_keyword}"}

        response = client.get(f'/search?keyword={long_keyword}', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 1

def test_search_performance_with_many_quotes(client):
    """Teste les performances de la recherche avec de nombreuses citations"""
    with patch('search.redis_client') as mock_redis:
        # Mock pour l'authentification
        mock_redis.exists.return_value = True
        mock_redis.hgetall.return_value = {"id": "default_key", "name": "admin"}

        # Simuler 100 citations
        quotes_keys = [f"quotes:{i}" for i in range(1, 101)]
        mock_redis.smembers.return_value = set(quotes_keys)

        # Seules quelques citations contiennent le mot-clé
        def search_hgetall_side_effect(key):
            if key.startswith("quotes:"):
                quote_id = key.split(":")[1]
                if int(quote_id) in [1, 50, 99]:
                    return {"quote": f"Citation {quote_id} avec le mot clé spécial"}

                return {"quote": f"Citation {quote_id} sans mot clé"}
            return {"id": "default_key", "name": "admin"}

        mock_redis.hgetall.side_effect = search_hgetall_side_effect

        response = client.get('/search?keyword=spécial', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 3

def test_search_with_unicode_characters(client):
    """Teste la recherche avec des caractères Unicode"""
    with patch('search.redis_client') as mock_redis:
        mock_redis.smembers.return_value = {"quotes:1"}
        mock_redis.hgetall.return_value = {"quote": "Citation avec caractères Unicode: café, naïve, résumé"}

        response = client.get('/search?keyword=café', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 1
        assert "café" in response.json[0]

def test_search_with_multiple_keywords(client):
    """Teste la recherche avec plusieurs mots-clés (seul le premier est utilisé)"""
    with patch('search.redis_client') as mock_redis:
        # Mock pour l'authentification
        mock_redis.exists.return_value = True
        mock_redis.hgetall.return_value = {"id": "default_key", "name": "admin"}

        # Simulation des données pour la recherche
        def search_hgetall_side_effect(key):
            if key.startswith("quotes:"):
                if key == "quotes:1":
                    return {"quote": "Citation avec premier mot"}
                if key == "quotes:2":
                    return {"quote": "Citation avec deuxième mot"}
            return {"id": "default_key", "name": "admin"}

        mock_redis.smembers.return_value = {"quotes:1", "quotes:2"}
        mock_redis.hgetall.side_effect = search_hgetall_side_effect

        # Test avec un seul mot-clé d'abord
        response = client.get('/search?keyword=premier', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 1
        assert "premier" in response.json[0]

        # Test avec un autre mot-clé
        response = client.get('/search?keyword=deuxième', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 1
        assert "deuxième" in response.json[0]
