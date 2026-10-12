def validate_student(student_id, name, email):
    if not str(student_id).strip():
        raise ValueError("Student ID is required")
    if not str(name).strip():
        raise ValueError("Student name is required")
    if "@" not in str(email) or "." not in str(email).split("@")[-1]:
        raise ValueError("A valid email is required")

    return {
        "student_id": str(student_id).strip(),
        "name": str(name).strip(),
        "email": str(email).strip()
    }


def calculate_gpa(marks):
    if not marks:
        raise ValueError("At least one mark is required")

    numeric_marks = []
    for mark in marks:
        if isinstance(mark, bool) or not isinstance(mark, (int, float)):
            raise ValueError("Marks must be numbers")
        if mark < 0 or mark > 100:
            raise ValueError("Marks must be between 0 and 100")
        numeric_marks.append(mark)

    average = sum(numeric_marks) / len(numeric_marks)
    return round(average / 10, 2)
