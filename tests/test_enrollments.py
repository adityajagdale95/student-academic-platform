import pytest
from app import create_app
import database.db as database


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def setup_student_and_courses(client):
    client.post("/students", json={
        "student_id": "STU100",
        "name": "Test Student",
        "email": "student100@example.com"
    })

    client.post("/courses", json={
        "course_id": "C101",
        "name": "Computer Science",
        "credits": 10
    })

    client.post("/courses", json={
        "course_id": "C102",
        "name": "Data Science",
        "credits": 9
    })


def test_successful_enrollment(client):
    setup_student_and_courses(client)

    response = client.post("/enrollments", json={
        "student_id": "STU100",
        "course_id": "C101",
        "semester": "Semester 3"
    })

    assert response.status_code == 201


def test_enrollment_rejects_over_18_credits(client):
    setup_student_and_courses(client)

    first = client.post("/enrollments", json={
        "student_id": "STU100",
        "course_id": "C101",
        "semester": "Semester 3"
    })
    second = client.post("/enrollments", json={
        "student_id": "STU100",
        "course_id": "C102",
        "semester": "Semester 3"
    })

    assert first.status_code == 201
    assert second.status_code == 400
    assert "18" in second.get_json()["error"]


def test_duplicate_enrollment_is_rejected(client):
    setup_student_and_courses(client)
    payload = {
        "student_id": "STU100",
        "course_id": "C101",
        "semester": "Semester 3"
    }

    assert client.post("/enrollments", json=payload).status_code == 201
    assert client.post("/enrollments", json=payload).status_code == 409


def test_enrollment_rejects_unknown_student(client):
    client.post("/courses", json={
        "course_id": "C101",
        "name": "Computer Science",
        "credits": 3
    })

    response = client.post("/enrollments", json={
        "student_id": "UNKNOWN",
        "course_id": "C101",
        "semester": "Semester 3"
    })

    assert response.status_code == 404
