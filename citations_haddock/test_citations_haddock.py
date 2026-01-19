import pytest
from unittest.mock import patch
from citations_haddock import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_hello_world(client):
    with patch('citations_haddock.redis_client'):
        response = client.get('/')
        assert response.status_code == 200
        assert response.json == {"message": "Hello World!"}

def test_get_users(client):
    with patch('citations_haddock.redis_client') as mock_redis:
        mock_redis.smembers.return_value = {b'users:1'}
        mock_redis.hgetall.return_value = {"id": "1", "name": "test_user", "password": "test_password"}

        response = client.get('/users', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['name'] == 'test_user'

def test_add_user(client):
    with patch('citations_haddock.redis_client') as mock_redis:
        response = client.post('/users',
                                headers={'Authorization': 'default_key'},
                                json={"id": "2", "name": "new_user", "password": "new_password"})
        assert response.status_code == 201
        assert response.json == {"message": "Utilisateur ajouté"}

def test_get_quotes(client):
    with patch('citations_haddock.redis_client') as mock_redis:
        mock_redis.smembers.return_value = {b'quotes:1'}
        mock_redis.hgetall.return_value = {"quote": "Test quote 1"}

        response = client.get('/quotes')
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['quote'] == 'Test quote 1'

def test_add_quote(client):
    with patch('citations_haddock.redis_client') as mock_redis:
        mock_redis.incr.return_value = 1

        response = client.post('/quotes',
                                headers={'Authorization': 'default_key'},
                                json={"user_id": "1", "quote": "New test quote"})
        assert response.status_code == 201
        assert response.json == {"message": "Citation ajoutée", "id": 1}

def test_delete_quote(client):
    with patch('citations_haddock.redis_client') as mock_redis:
        mock_redis.hexists.return_value = True

        response = client.delete('/quotes/1', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert response.json == {"message": "Citation supprimée"}

def test_search_quotes(client):
    with patch('citations_haddock.redis_client') as mock_redis:
        mock_redis.smembers.return_value = {b'quotes:1'}
        mock_redis.hgetall.return_value = {"quote": "Test quote 1"}

        response = client.get('/search?keyword=Test', headers={'Authorization': 'default_key'})
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0] == 'Test quote 1'
