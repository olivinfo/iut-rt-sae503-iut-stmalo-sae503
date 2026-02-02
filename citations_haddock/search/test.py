import pytest
from unittest.mock import patch
from search_service import app as flask_app

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
    assert response.json == {"error": "Unauthorized"}

def test_search_quotes_success(client):
    """Teste une recherche réussie avec Mock de Redis"""
    with patch('search_service.redis_client') as mock_redis:
        # Simulation des données dans Redis
        mock_redis.smembers.return_value = {"quotes:1", "quotes:2"}
        
        # Simulation du retour de hgetall pour chaque citation
        mock_redis.hgetall.side_effect = [
            {"quote": "Mille sabords !"},
            {"quote": "Tonnerre de Brest !"}
        ]

        response = client.get('/search?keyword=Brest', headers={'Authorization': 'default_key'})
        
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0] == "Tonnerre de Brest !"

def test_search_quotes_no_results(client):
    """Teste une recherche qui ne trouve rien"""
    with patch('search_service.redis_client') as mock_redis:
        mock_redis.smembers.return_value = {"quotes:1"}
        mock_redis.hgetall.return_value = {"quote": "Mille sabords !"}

        response = client.get('/search?keyword=Inconnu', headers={'Authorization': 'default_key'})
        
        assert response.status_code == 200
        assert response.json == []