import pytest
from app.services.student_service import validate_student, calculate_gpa


def test_validate_student():
    student = validate_student("S101", "Amit Patil", "amit@example.com")
    assert student["student_id"] == "S101"
    assert student["name"] == "Amit Patil"


def test_invalid_email():
    with pytest.raises(ValueError):
        validate_student("S101", "Amit", "invalid-email")


def test_calculate_gpa():
    assert calculate_gpa([80, 90]) == 8.5


def test_calculate_gpa_rejects_out_of_range_marks():
    with pytest.raises(ValueError):
        calculate_gpa([80, 110])


def test_calculate_gpa_rejects_empty_marks():
    with pytest.raises(ValueError):
        calculate_gpa([])
