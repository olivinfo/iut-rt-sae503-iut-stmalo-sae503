import logging
from typing import Optional, Dict, Any
import redis
import requests

# Configuration des URLs de base
QUOTES_URL = "http://localhost:5000" # 5001
SEARCH_URL = "http://localhost:5000" # 5002
USERS_URL = "http://localhost:5000"

# Clé d'authentification
ADMIN_KEY = "default_key"
HEADERS = {"Authorization": ADMIN_KEY}

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Nettoyage de Redis avant les tests
def cleanup_redis():
    try:
        r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        r.flushdb()
        logger.info("Redis nettoyé avec succès.")
    except Exception as e:
        logger.error("Erreur lors du nettoyage de Redis : %s", e)

# Fonction pour effectuer une requête avec gestion des erreurs
def make_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, str]] = None,
) -> requests.Response:
    try:
        response = requests.request(method, url, headers=headers, json=json, params=params, timeout=2)
        logger.info(f"Requête {method} {url} : {response.status_code}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la requête {method} {url} : {e}")
        raise

# Tests fonctionnels
def test_hello_world():
    """Teste l'endpoint de base du service utilisateurs."""
    response = make_request("GET", f"{USERS_URL}/")
    assert response.status_code == 200, f"Échec : {response.text}"
    # assert response.json() == {"message":"Hello World"}

def test_add_user():
    """Teste l'ajout d'un utilisateur."""
    user_data = {"id": "100", "name": "Test User", "password": "test"}
    response = make_request("POST", f"{USERS_URL}/users", headers=HEADERS, json=user_data)
    assert response.status_code == 201, f"Échec : {response.text}"
    assert response.json() == {"message": "Utilisateur ajouté"}

def test_add_user_missing_name():
    """Teste l'ajout d'un utilisateur sans nom."""
    user_data = {"id": "2", "password": "test"}
    response = make_request("POST", f"{USERS_URL}/users", headers=HEADERS, json=user_data)
    assert response.status_code == 400, f"Échec : {response.text}"
    assert "ID et nom sont requis" in response.json()["error"]

def test_add_user_missing_id():
    """Teste l'ajout d'un utilisateur sans ID."""
    user_data = {"name": "Test User", "password": "test"}
    response = make_request("POST", f"{USERS_URL}/users", headers=HEADERS, json=user_data)
    assert response.status_code == 400, f"Échec : {response.text}"
    assert "ID et nom sont requis" in response.json()["error"]

def test_get_users():
    """Teste la récupération de tous les utilisateurs."""
    response = make_request("GET", f"{USERS_URL}/users", headers=HEADERS)
    assert response.status_code == 200, f"Échec : {response.text}"
    assert len(response.json()) >= 1, "Aucun utilisateur trouvé"

def test_get_users_unauthorized():
    """Teste la récupération des utilisateurs sans autorisation."""
    response = make_request("GET", f"{USERS_URL}/users")
    assert response.status_code == 401, f"Échec : {response.text}"
    # assert response.json() == {"error": "Unauthorized"}

def test_user_login_success():
    """Teste la connexion réussie d'un utilisateur."""
    login_data = {"name": "Alice", "password": "inWonderland"}
    response = make_request("POST", f"{USERS_URL}/users/login", json=login_data)
    assert response.status_code == 200, f"Échec : {response.text}"
    assert "token" in response.json(), "Token non retourné"
    assert "user_id" in response.json(), "User ID non retourné"
    assert response.json()["user_id"] == "0", "User ID incorrect"

def test_user_login_wrong_password():
    """Teste la connexion avec un mot de passe incorrect."""
    login_data = {"name": "Alice", "password": "wrongPassword"}
    response = make_request("POST", f"{USERS_URL}/users/login", json=login_data)
    assert response.status_code == 401, f"Échec : {response.text}"
    assert "error" in response.json(), "Message d'erreur non retourné"

def test_user_login_nonexistent_user():
    """Teste la connexion avec un utilisateur qui n'existe pas."""
    login_data = {"name": "UnknownUser", "password": "somePassword"}
    response = make_request("POST", f"{USERS_URL}/users/login", json=login_data)
    assert response.status_code == 401, f"Échec : {response.text}"
    assert "error" in response.json(), "Message d'erreur non retourné"

def test_user_login_missing_credentials():
    """Teste la connexion sans nom ou mot de passe."""
    # Sans nom
    login_data = {"password": "somePassword"}
    response = make_request("POST", f"{USERS_URL}/users/login", json=login_data)
    assert response.status_code == 400, f"Échec : {response.text}"
    assert "error" in response.json(), "Message d'erreur non retourné"

    # Sans mot de passe
    login_data = {"name": "Alice"}
    response = make_request("POST", f"{USERS_URL}/users/login", json=login_data)
    assert response.status_code == 400, f"Échec : {response.text}"
    assert "error" in response.json(), "Message d'erreur non retourné"

def test_user_login_and_use_token():
    """Teste la connexion d'un utilisateur et l'utilisation du token pour des requêtes authentifiées."""
    # D'abord, connecter l'utilisateur
    login_data = {"name": "Bob", "password": "squarePants"}
    login_response = make_request("POST", f"{USERS_URL}/users/login", json=login_data)
    assert login_response.status_code == 200, f"Échec de connexion : {login_response.text}"

    token = login_response.json()["token"]
    user_headers = {"Authorization": token}

    # Ensuite, utiliser le token pour accéder à une route protégée
    response = make_request("GET", f"{USERS_URL}/users", headers=user_headers)
    assert response.status_code == 200, f"Échec d'accès avec token : {response.text}"
    assert len(response.json()) >= 1, "Aucun utilisateur trouvé"

def test_add_quote():
    """Teste l'ajout d'une citation."""
    quote_data = {"user_id": "1", "quote": "Citation de test"}
    response = make_request("POST", f"{QUOTES_URL}/quotes", headers=HEADERS, json=quote_data)
    assert response.status_code == 201, f"Échec : {response.text}"
    assert "id" in response.json(), "ID de la citation non retourné"

def test_add_quote_missing_user_id():
    """Teste l'ajout d'une citation sans user_id."""
    quote_data = {"quote": "Citation de test"}
    response = make_request("POST", f"{QUOTES_URL}/quotes", headers=HEADERS, json=quote_data)
    assert response.status_code == 400, f"Échec : {response.text}"
    assert "user_id et quote sont requis" in response.json()["error"]

def test_add_quote_missing_quote():
    """Teste l'ajout d'une citation sans texte."""
    quote_data = {"user_id": "1"}
    response = make_request("POST", f"{QUOTES_URL}/quotes", headers=HEADERS, json=quote_data)
    assert response.status_code == 400, f"Échec : {response.text}"
    assert "user_id et quote sont requis" in response.json()["error"]

def test_add_quote_unauthorized():
    """Teste l'ajout d'une citation sans autorisation."""
    quote_data = {"user_id": "1", "quote": "Citation de test"}
    response = make_request("POST", f"{QUOTES_URL}/quotes", json=quote_data)
    assert response.status_code == 401, f"Échec : {response.text}"
    # assert response.json() == {"error": "Unauthorized"}

def test_delete_quote():
    """Teste la suppression d'une citation."""
    # D'abord, ajoutons une citation pour avoir un ID valide
    quote_data = {"user_id": "1", "quote": "Citation à supprimer"}
    add_response = make_request("POST", f"{QUOTES_URL}/quotes", headers=HEADERS, json=quote_data)
    quote_id = add_response.json()["id"]
    # Maintenant, supprimons la citation
    response = make_request("DELETE", f"{QUOTES_URL}/quotes/{quote_id}", headers=HEADERS)
    assert response.status_code == 200, f"Échec : {response.text}"
    assert response.json() == {"message": "Citation supprimée"}

def test_delete_quote_not_found():
    """Teste la suppression d'une citation qui n'existe pas."""
    quote_id = 9999  # ID qui n'existe probablement pas
    response = make_request("DELETE", f"{QUOTES_URL}/quotes/{quote_id}", headers=HEADERS)
    assert response.status_code == 404, f"Échec : {response.text}"
    assert "non trouvée" in response.json()["error"]

def test_delete_quote_unauthorized():
    """Teste la suppression d'une citation sans autorisation."""
    quote_id = 1
    response = make_request("DELETE", f"{QUOTES_URL}/quotes/{quote_id}")
    assert response.status_code == 401, f"Échec : {response.text}"
    # assert response.json() == {"error": "Unauthorized"}

def test_search_quotes():
    """Teste la recherche de citations."""
    keyword = "test"
    response = make_request("GET", f"{SEARCH_URL}/search", headers=HEADERS, params={"keyword": keyword})
    assert response.status_code == 200, f"Échec : {response.text}"
    assert isinstance(response.json(), list), "La réponse n'est pas une liste"

def test_search_quotes_no_keyword():
    """Teste la recherche sans mot-clé."""
    response = make_request("GET", f"{SEARCH_URL}/search", headers=HEADERS)
    assert response.status_code == 400, f"Échec : {response.text}"
    assert response.json() == {"error": "Mot-clé requis"}

def test_search_quotes_unauthorized():
    """Teste la recherche sans autorisation."""
    keyword = "test"
    response = make_request("GET", f"{SEARCH_URL}/search", params={"keyword": keyword})
    assert response.status_code == 401, f"Échec : {response.text}"
    # assert response.json() == {"error": "Unauthorized"}

def test_search_quotes_no_results():
    """Teste la recherche qui ne retourne aucun résultat."""
    keyword = "motcléinexistant"
    response = make_request("GET", f"{SEARCH_URL}/search", headers=HEADERS, params={"keyword": keyword})
    assert response.status_code == 200, f"Échec : {response.text}"
    assert response.json() == [], "La réponse devrait être une liste vide"

def test_unauthorized_access():
    """Teste l'accès non autorisé."""
    response = make_request("POST", f"{QUOTES_URL}/quotes", json={"user_id": "1", "quote": "Test"})
    assert response.status_code == 401, f"Échec : {response.text}"
    # assert response.json() == {"error": "Unauthorized"}

def test_missing_data():
    """Teste l'ajout d'une citation sans données requises."""
    response = make_request("POST", f"{QUOTES_URL}/quotes", headers=HEADERS, json={"user_id": "1"})
    assert response.status_code == 400, f"Échec : {response.text}"
    assert "quote" in response.json()["error"].lower()

def test_integration_workflow():
    """Teste un workflow complet d'intégration."""
    # 1. Ajouter un utilisateur
    user_data = {"id": "100", "name": "Integration Test User", "password": "test123"}
    user_response = make_request("POST", f"{USERS_URL}/users", headers=HEADERS, json=user_data)
    assert user_response.status_code == 201

    # 2. Ajouter une citation pour cet utilisateur
    quote_data = {"user_id": "100", "quote": "Citation d'intégration"}
    quote_response = make_request("POST", f"{QUOTES_URL}/quotes", headers=HEADERS, json=quote_data)
    assert quote_response.status_code == 201
    quote_id = quote_response.json()["id"]

    # 3. Rechercher la citation
    search_response = make_request("GET", f"{SEARCH_URL}/search", headers=HEADERS, params={"keyword": "intégration"})
    assert search_response.status_code == 200
    assert len(search_response.json()) >= 1

    # 4. Supprimer la citation
    delete_response = make_request("DELETE", f"{QUOTES_URL}/quotes/{quote_id}", headers=HEADERS)
    assert delete_response.status_code == 200

    # 5. Vérifier que la citation a été supprimée
    search_after_delete=make_request("GET", f"{SEARCH_URL}/search", headers=HEADERS, params={"keyword": "intégration"})
    assert search_after_delete.status_code == 200
    # La citation ne devrait plus être trouvée
    assert "Citation d'intégration" not in search_after_delete.json()


if __name__ == "__main__":
    logger.info("Nettoyage de Redis avant les tests...")
    cleanup_redis()

    logger.info("Démarrage des tests fonctionnels...")
    try:
        # Tests utilisateurs
        test_hello_world()
        test_add_user()
        test_add_user_missing_name()
        test_add_user_missing_id()
        test_get_users()
        test_get_users_unauthorized()
        test_user_login_success()
        test_user_login_wrong_password()
        test_user_login_nonexistent_user()
        test_user_login_missing_credentials()
        test_user_login_and_use_token()

        # Tests citations
        test_add_quote()
        test_add_quote_missing_user_id()
        test_add_quote_missing_quote()
        test_add_quote_unauthorized()
        test_delete_quote()
        test_delete_quote_not_found()
        test_delete_quote_unauthorized()

        # Tests recherche
        test_search_quotes()
        test_search_quotes_no_keyword()
        test_search_quotes_unauthorized()
        test_search_quotes_no_results()

        # Tests d'intégration
        test_integration_workflow()

        logger.info("Tous les tests ont réussi !")
    except AssertionError as e:
        logger.error(f"Test échoué : {e}")
    except Exception as e:
        logger.error(f"Erreur inattendue : {e}")
