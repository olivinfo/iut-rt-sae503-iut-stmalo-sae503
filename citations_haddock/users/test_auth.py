"""
Tests unitaires spécifiques pour l'authentification du service utilisateurs
"""

import pytest
from users import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_authentication_with_alice_key(client):
    """Teste l'authentification avec la clé d'Alice (inWonderland)"""
    # Dans le système actuel, seule default_key est valide
    response = client.get('/users', headers={'Authorization': 'inWonderland'})
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

def test_authentication_with_wrong_key(client):
    """Teste l'authentification avec une clé incorrecte"""
    response = client.get('/users', headers={'Authorization': 'wrong_key'})
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

def test_authentication_with_empty_key(client):
    """Teste l'authentification avec une clé vide"""
    response = client.get('/users', headers={'Authorization': ''})
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

def test_authentication_missing_header(client):
    """Teste l'authentification sans en-tête Authorization"""
    response = client.get('/users')
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

def test_valid_authentication_for_all_endpoints(client):
    """Teste que la clé valide fonctionne pour tous les endpoints protégés"""
    headers = {'Authorization': 'default_key'}

    # Test GET /users
    response = client.get('/users', headers=headers)
    assert response.status_code == 200

    # Test POST /users
    user_data = {"id": "1", "name": "Test User", "password": "test"}
    response = client.post('/users', headers=headers, json=user_data)
    assert response.status_code == 201

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
