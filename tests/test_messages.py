import os
from dotenv import load_dotenv
load_dotenv(".env.test")

import pytest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from extensions import db
from models.user import User


@pytest.fixture
def client():
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret-key-that-is-long-enough"

    with app.app_context():
        db.create_all()
        yield app.test_client(), app
        db.session.remove()
        db.drop_all()


def create_user_and_token(role, email, phone):
    user = User(
        full_name="Test User",
        email=email,
        password_hash=generate_password_hash("password123"),
        role=role,
        phone=phone,
        location="Nairobi"
    )
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return token, user.id


def test_send_message(client):
    test_client, app = client
    with app.app_context():
        sender_token, _ = create_user_and_token("client", "sender@test.com", "0700000001")
        receiver_token, receiver_id = create_user_and_token("worker", "receiver@test.com", "0700000002")
    response = test_client.post("/messages/", json={
        "receiver_id": receiver_id,
        "content": "Hello, are you available?"
    }, headers={"Authorization": f"Bearer {sender_token}"})
    assert response.status_code == 201
    assert response.get_json()["data"]["content"] == "Hello, are you available?"


def test_send_message_no_auth(client):
    test_client, app = client
    response = test_client.post("/messages/", json={
        "receiver_id": 1,
        "content": "Hello"
    })
    assert response.status_code == 401


def test_send_message_missing_fields(client):
    test_client, app = client
    with app.app_context():
        token, _ = create_user_and_token("client", "user@test.com", "0700000003")
    response = test_client.post("/messages/", json={
        "content": "Hello"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400


def test_get_conversations(client):
    test_client, app = client
    with app.app_context():
        token, _ = create_user_and_token("client", "user2@test.com", "0700000004")
    response = test_client.get("/messages/conversations", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_conversation_user_not_found(client):
    test_client, app = client
    with app.app_context():
        token, _ = create_user_and_token("client", "user3@test.com", "0700000005")
    response = test_client.get("/messages/999", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 404