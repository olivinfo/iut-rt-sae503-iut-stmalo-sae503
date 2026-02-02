import pytest
from unittest.mock import patch
from quote_service import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_add_quote_success(client):
    """Vérifie l'ajout d'une citation et la structure Redis"""
    with patch('quote_service.redis_client') as mock_redis:
        mock_redis.incr.return_value = 10  # Simule l'ID généré
        
        payload = {"user_id": "1", "quote": "Mille sabords !"}
        response = client.post('/quotes', 
                               headers={'Authorization': 'default_key'},
                               json=payload)
        
        assert response.status_code == 201
        assert response.json['id'] == 10
        # On vérifie que hset est appelé avec la bonne clé formatée
        mock_redis.hset.assert_called_with("quotes:10", mapping=payload)
        # On vérifie l'ajout à l'index pour le service search
        mock_redis.sadd.assert_called_with("quotes", "quotes:10")

def test_add_quote_missing_data(client):
    """Vérifie l'erreur si le texte de la citation manque"""
    response = client.post('/quotes', 
                           headers={'Authorization': 'default_key'},
                           json={"user_id": "1"}) # quote manquante
    assert response.status_code == 400
    assert "user_id et quote sont requis" in response.json['error']

def test_delete_quote_success(client):
    """Vérifie la suppression complète (Clé + Index)"""
    with patch('quote_service.redis_client') as mock_redis:
        # On simule que la citation existe
        mock_redis.hexists.return_value = True
        
        response = client.delete('/quotes/5', headers={'Authorization': 'default_key'})
        
        assert response.status_code == 200
        # Vérifie que la clé est supprimée ET retirée du set d'indexation
        mock_redis.delete.assert_called_with("quotes:5")
        mock_redis.srem.assert_called_with("quotes", "quotes:5")

def test_delete_quote_not_found(client):
    """Vérifie l'erreur 404 si la citation n'existe pas"""
    with patch('quote_service.redis_client') as mock_redis:
        mock_redis.hexists.return_value = False
        
        response = client.delete('/quotes/99', headers={'Authorization': 'default_key'})
        assert response.status_code == 404
        assert "non trouvée" in response.json['error']

def test_unauthorized_access(client):
    """Vérifie que le décorateur require_auth fonctionne toujours"""
    response = client.post('/quotes', json={"quote": "test"})
    assert response.status_code == 401