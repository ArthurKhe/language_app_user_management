import json
import pytest
from main import app
from fastapi.testclient import TestClient
from mongomock import MongoClient

@pytest.fixture
def prefix_url():
    return "/api/v1/"


@pytest.fixture
def test_client():
    return TestClient(app)


def test_get_users_returns_list(test_client, prefix_url):
    response = test_client.get(f"{prefix_url}user/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user_returns_user(test_client, prefix_url):
    # assume there is a user with id 1 in the database
    response = test_client.get(f"{prefix_url}user/1")
    assert response.status_code == 200
    assert response.json()["user_id"] == 1


def test_get_user_not_found(test_client, prefix_url):
    # assume there is no user with id 999 in the database
    response = test_client.get(f"{prefix_url}user/999")
    assert response.status_code == 404
    assert "user (999) not existed" in response.text


def test_create_user(test_client, prefix_url):
    # assume the user does not exist in the database yet
    user_data = {"user_id": 123, "chat_id": 456}

    # Create mock mongodb client and collection
    mongo_client = MongoClient()
    mongo_collection = mongo_client.language_app.users

    with app.container.user_repository.override(lambda: MongoUserRepository(mongo_collection)):
        response = test_client.post("/api/v1/user/", params=user_data)

        assert response.status_code == 201
        assert json.loads(response.content)["user_id"] == user_data["user_id"]
        assert json.loads(response.content)["chat_id"] == user_data["chat_id"]


def test_create_existing_user(test_client, prefix_url):
    # assume the user already exists in the database
    user_data = {"user_id": 1, "chat_id": 456}
    response = test_client.post(f"{prefix_url}user/", params=user_data)
    assert response.status_code == 200
    assert "user (1) existing" in response.text


def test_create_user_with_invalid_data(test_client, prefix_url):
    # assume the user data is missing the chat_id field
    user_data = {"user_id": 123}
    response = test_client.post(f"{prefix_url}user/", json=user_data)
    assert response.status_code == 422
