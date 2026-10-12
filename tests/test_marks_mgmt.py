import pytest
from app import create_app
import database.db as database


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_marks.db"
    monkeypatch.setattr(database, "DB_PATH", test_db)

    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def registered_student(client):
    response = client.post(
        "/students",
        json={
            "student_id": "STU010",
            "name": "Test Student",
            "email": "test10@example.com"
        }
    )
    assert response.status_code == 201
    return "STU010"


def test_add_marks(client, registered_student):
    response = client.post(
        "/students/STU010/marks",
        json={"subject": "Math", "marks": 80}
    )
    assert response.status_code == 201
    assert response.json["marks"] == 80


def test_get_marks(client, registered_student):
    client.post(
        "/students/STU010/marks",
        json={"subject": "Math", "marks": 80}
    )

    response = client.get("/students/STU010/marks")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["subject"] == "Math"


def test_invalid_marks_rejected(client, registered_student):
    response = client.post(
        "/students/STU010/marks",
        json={"subject": "Math", "marks": 150}
    )
    assert response.status_code == 400


def test_gpa_calculation(client, registered_student):
    client.post(
        "/students/STU010/marks",
        json={"subject": "Math", "marks": 80}
    )
    client.post(
        "/students/STU010/marks",
        json={"subject": "Science", "marks": 90}
    )

    response = client.get("/students/STU010/gpa")
    assert response.status_code == 200
    assert response.json["average_marks"] == 85
    assert response.json["gpa"] == 8.5


def test_marks_for_missing_student(client):
    response = client.post(
        "/students/UNKNOWN/marks",
        json={"subject": "Math", "marks": 80}
    )
    assert response.status_code == 404
