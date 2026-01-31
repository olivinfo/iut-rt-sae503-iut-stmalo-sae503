"""
Tests unitaires spécifiques pour l'authentification du service citations
"""

import pytest
from quotes import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_authentication_with_alice_key(client):
    """Teste l'authentification avec la clé d'Alice (inWonderland)"""
    quote_data = {"user_id": "1", "quote": "Test quote"}
    response = client.post('/quotes', headers={'Authorization': 'inWonderland'}, json=quote_data)
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

def test_authentication_with_wrong_key(client):
    """Teste l'authentification avec une clé incorrecte"""
    quote_data = {"user_id": "1", "quote": "Test quote"}
    response = client.post('/quotes', headers={'Authorization': 'wrong_key'}, json=quote_data)
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

def test_authentication_with_empty_key(client):
    """Teste l'authentification avec une clé vide"""
    quote_data = {"user_id": "1", "quote": "Test quote"}
    response = client.post('/quotes', headers={'Authorization': ''}, json=quote_data)
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

def test_authentication_missing_header(client):
    """Teste l'authentification sans en-tête Authorization"""
    quote_data = {"user_id": "1", "quote": "Test quote"}
    response = client.post('/quotes', json=quote_data)
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

def test_valid_authentication_for_all_endpoints(client):
    """Teste que la clé valide fonctionne pour tous les endpoints protégés"""
    headers = {'Authorization': 'default_key'}

    # Test POST /quotes
    quote_data = {"user_id": "1", "quote": "Test quote"}
    response = client.post('/quotes', headers=headers, json=quote_data)
    assert response.status_code == 201

    # Test DELETE /quotes/:id (on suppose que l'ID 1 existe)
    response = client.delete('/quotes/1', headers=headers)
    # Note: Cela pourrait échouer si la citation n'existe pas, mais c'est pour tester l'auth
    assert response.status_code in [200, 404]  # 200 si supprimé, 404 si non trouvé

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
