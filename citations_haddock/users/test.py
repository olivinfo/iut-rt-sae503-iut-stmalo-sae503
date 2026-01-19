import pytest
from unittest.mock import patch
from user_service import app as flask_app  # Assurez-vous que le fichier se nomme user_service.py

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_hello_world(client):
    """Vérifie que le service répond correctement sur la racine"""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"message": "User Service Online"}

def test_get_users_unauthorized(client):
    """Vérifie que l'accès est refusé sans authentification"""
    response = client.get('/users')
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

def test_get_users_success(client):
    """Vérifie la récupération de la liste des utilisateurs"""
    with patch('user_service.redis_client') as mock_redis:
        # On simule la présence de deux clés d'utilisateurs
        mock_redis.smembers.return_value = {"users:1", "users:2"}
        # On simule le contenu de chaque utilisateur
        mock_redis.hgetall.side_effect = [
            {"id": "1", "name": "Tintin", "password": "milou"},
            {"id": "2", "name": "Haddock", "password": "rhum"}
        ]

        response = client.get('/users', headers={'Authorization': 'default_key'})
        
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['name'] == "Tintin"

def test_add_user_success(client):
    """Vérifie l'ajout d'un nouvel utilisateur"""
    with patch('user_service.redis_client') as mock_redis:
        new_user = {"id": "3", "name": "Tournesol", "password": "pendule"}
        
        response = client.post('/users', 
                               headers={'Authorization': 'default_key'},
                               json=new_user)
        
        assert response.status_code == 201
        assert response.json == {"message": "Utilisateur ajouté"}
        # Vérifie que les méthodes Redis ont bien été appelées
        assert mock_redis.hset.called
        assert mock_redis.sadd.called

def test_add_user_invalid_data(client):
    """Vérifie l'erreur si des données obligatoires manquent"""
    response = client.post('/users', 
                           headers={'Authorization': 'default_key'},
                           json={"id": "4"}) # Il manque le nom
    
    assert response.status_code == 400
    assert "ID et nom sont requis" in response.json['error']