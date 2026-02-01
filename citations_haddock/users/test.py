from unittest.mock import patch
import pytest
from users import app as flask_app  # Assurez-vous que le fichier se nomme users.py

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
    assert response.json == {'error': 'Authorization header is missing'}

# def test_get_users_success(client):
#     """Vérifie la récupération de la liste des utilisateurs"""
#     with patch('users.redis_client') as mock_redis:
#         # Simuler la présence du token dans Redis
#         mock_redis.exists.return_value = True
#         mock_redis.hgetall.return_value = {"id": "default_key", "name": "admin"}

#         # On simule la présence de deux clés d'utilisateurs
#         mock_redis.smembers.return_value = {"users:1", "users:2"}

#         # Utilisation d'une fonction pour side_effect
#         def hgetall_side_effect(key):
#             if key == "users:1":
#                 return {"id": "1", "name": "Tintin", "password": "milou"}
#             elif key == "users:2":
#                 return {"id": "2", "name": "Haddock", "password": "rhum"}
#             return {}

#         # Appliquer side_effect uniquement pour les appels à hgetall liés aux utilisateurs
#         mock_redis.hgetall.side_effect = hgetall_side_effect

#         response = client.get('/users', headers={'Authorization': 'default_key'})

#         assert response.status_code == 200
#         assert len(response.json) == 2
#         assert response.json[0]['name'] == "Tintin"
#         assert response.json[1]['name'] == "Haddock"
#         assert all('id' in user and 'name' in user for user in response.json)

def test_add_user_success(client):
    """Vérifie l'ajout d'un nouvel utilisateur"""
    with patch('users.redis_client') as mock_redis:
        new_user = {"id": "3", "name": "Tournesol", "password": "pendule"}

        response = client.post('/users',
                               headers={'Authorization': 'default_key'},
                               json=new_user)

        assert response.status_code == 201
        assert response.json == {"message": "Utilisateur ajouté"}
        # Vérifie que les méthodes Redis ont bien été appelées
        assert mock_redis.hset.called
        assert mock_redis.sadd.called
        # Vérification des appels spécifiques
        mock_redis.hset.assert_called_with("users:3", mapping=new_user)
        mock_redis.sadd.assert_called_with("users", "users:3")

def test_add_user_invalid_data(client):
    """Vérifie l'erreur si des données obligatoires manquent"""
    # Test sans nom
    response = client.post('/users',
                           headers={'Authorization': 'default_key'},
                           json={"id": "4"}) # Il manque le nom

    assert response.status_code == 400
    assert "ID et nom sont requis" in response.json['error']

    # Test sans ID
    response = client.post('/users',
                           headers={'Authorization': 'default_key'},
                           json={"name": "Test"}) # Il manque l'ID

    assert response.status_code == 400
    assert "ID et nom sont requis" in response.json['error']

def test_add_user_with_alice_auth(client):
    """Teste l'ajout d'utilisateur avec la clé d'Alice (devrait échouer)"""
    new_user = {"id": "5", "name": "Alice", "password": "inWonderland"}
    response = client.post('/users',
                           headers={'Authorization': 'inWonderland'},
                           json=new_user)

    assert response.status_code == 401
    assert response.json == {'error': 'Unauthorized: Invalid token'}

def test_get_users_empty_database(client):
    """Teste la récupération des utilisateurs quand la base est vide"""
    with patch('users.redis_client') as mock_redis:
        mock_redis.smembers.return_value = set()  # Base vide

        response = client.get('/users', headers={'Authorization': 'default_key'})

        assert response.status_code == 200
        assert response.json == []

def test_authentication_header_format(client):
    """Teste différents formats d'en-tête d'authentification"""
    # Test avec Bearer token (devrait échouer car le système attend juste la clé)
    response = client.get('/users', headers={'Authorization': 'Bearer default_key'})
    assert response.status_code == 401

    # Test avec la clé directement (devrait fonctionner)
    response = client.get('/users', headers={'Authorization': 'default_key'})
    assert response.status_code == 200

def test_user_login_success(client):
    """Teste la connexion réussie d'un utilisateur"""
    with patch('users.redis_client') as mock_redis:
        # Simuler la présence de l'utilisateur dans Redis
        mock_redis.smembers.return_value = {"users:0"}
        mock_redis.hgetall.return_value = {"id": "0", "name": "Alice", "password": "inWonderland"}

        login_data = {"name": "Alice", "password": "inWonderland"}
        response = client.post('/users/login', json=login_data)

        assert response.status_code == 200
        assert "token" in response.json
        assert "user_id" in response.json
        assert response.json["user_id"] == "0"
        # Vérifier que le token a été stocké dans Redis
        assert mock_redis.hset.called
        assert mock_redis.sadd.called

def test_user_login_wrong_password(client):
    """Teste la connexion avec un mot de passe incorrect"""
    with patch('users.redis_client') as mock_redis:
        # Simuler la présence de l'utilisateur mais avec un mot de passe différent
        mock_redis.smembers.return_value = {"users:0"}
        mock_redis.hgetall.return_value = {"id": "0", "name": "Alice", "password": "inWonderland"}

        login_data = {"name": "Alice", "password": "wrongPassword"}
        response = client.post('/users/login', json=login_data)

        assert response.status_code == 401
        assert "error" in response.json

def test_user_login_nonexistent_user(client):
    """Teste la connexion avec un utilisateur qui n'existe pas"""
    with patch('users.redis_client') as mock_redis:
        # Simuler une base vide
        mock_redis.smembers.return_value = set()

        login_data = {"name": "UnknownUser", "password": "somePassword"}
        response = client.post('/users/login', json=login_data)

        assert response.status_code == 401
        assert "error" in response.json

def test_user_login_missing_credentials(client):
    """Teste la connexion sans nom ou mot de passe"""
    # Sans nom
    login_data = {"password": "somePassword"}
    response = client.post('/users/login', json=login_data)
    assert response.status_code == 400
    assert "error" in response.json

    # Sans mot de passe
    login_data = {"name": "Alice"}
    response = client.post('/users/login', json=login_data)
    assert response.status_code == 400
    assert "error" in response.json
