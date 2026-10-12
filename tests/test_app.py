import pytest
from app import create_app
import database.db as database


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_students.db"
    monkeypatch.setattr(database, "DB_PATH", test_db)

    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["status"] == "running"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_get_students(client):
    response = client.get("/students")
    assert response.status_code == 200
    assert response.json == []


def test_add_student(client):
    response = client.post(
        "/students",
        json={
            "student_id": "STU001",
            "name": "Rahul Sharma",
            "email": "rahul@example.com"
        }
    )

    assert response.status_code == 201
    assert response.json["student_id"] == "STU001"


def test_missing_student_fields(client):
    response = client.post(
        "/students",
        json={"student_id": "STU002"}
    )

    assert response.status_code == 400


def test_duplicate_student(client):
    student = {
        "student_id": "STU001",
        "name": "Rahul Sharma",
        "email": "rahul@example.com"
    }

    client.post("/students", json=student)
    response = client.post("/students", json=student)

    assert response.status_code == 409
