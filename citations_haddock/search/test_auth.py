"""
Tests unitaires spécifiques pour l'authentification du service recherche
"""

import pytest
from search import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_authentication_with_alice_key(client):
    """Teste l'authentification avec la clé d'Alice (inWonderland)"""
    response = client.get('/search?keyword=test', headers={'Authorization': 'inWonderland'})
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

def test_authentication_with_wrong_key(client):
    """Teste l'authentification avec une clé incorrecte"""
    response = client.get('/search?keyword=test', headers={'Authorization': 'wrong_key'})
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

def test_authentication_with_empty_key(client):
    """Teste l'authentification avec une clé vide"""
    response = client.get('/search?keyword=test', headers={'Authorization': ''})
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

def test_authentication_missing_header(client):
    """Teste l'authentification sans en-tête Authorization"""
    response = client.get('/search?keyword=test')
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

def test_valid_authentication_for_search(client):
    """Teste que la clé valide fonctionne pour la recherche"""
    headers = {'Authorization': 'default_key'}
    response = client.get('/search?keyword=test', headers=headers)
    # Le code 200 ou 400 (si keyword manquant) est acceptable pour tester l'auth
    assert response.status_code in [200, 400]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
