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


def get_token(app):
    user = User(
        full_name="Test Client",
        email="client@test.com",
        password_hash=generate_password_hash("password123"),
        role="client",
        phone="0700000001",
        location="Nairobi"
    )
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return token, user.id


def test_create_job(client):
    test_client, app = client
    with app.app_context():
        token, _ = get_token(app)
    response = test_client.post("/jobs/", json={
        "title": "Plumber Needed",
        "description": "Fix kitchen sink",
        "budget": 1500.0,
        "location": "Nairobi"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.get_json()["job"]["title"] == "Plumber Needed"


def test_list_jobs(client):
    test_client, app = client
    response = test_client.get("/jobs/")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_job_not_found(client):
    test_client, app = client
    response = test_client.get("/jobs/999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Job not found"


def test_create_job_missing_fields(client):
    test_client, app = client
    with app.app_context():
        token, _ = get_token(app)
    response = test_client.post("/jobs/", json={
        "title": "Incomplete Job"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400


def test_create_job_no_auth(client):
    test_client, app = client
    response = test_client.post("/jobs/", json={
        "title": "Plumber Needed",
        "description": "Fix kitchen sink",
        "budget": 1500.0,
        "location": "Nairobi"
    })
    assert response.status_code == 401


def test_delete_job_unauthorized(client):
    test_client, app = client
    with app.app_context():
        token, _ = get_token(app)
    job_response = test_client.post("/jobs/", json={
        "title": "Plumber Needed",
        "description": "Fix sink",
        "budget": 1500.0,
        "location": "Nairobi"
    }, headers={"Authorization": f"Bearer {token}"})
    job_id = job_response.get_json()["job"]["id"]
    response = test_client.delete(f"/jobs/{job_id}")
    assert response.status_code == 401