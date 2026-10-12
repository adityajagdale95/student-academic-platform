from flask import Flask, jsonify, request
import sqlite3

from database.db import (
    init_db,
    add_student as save_student,
    get_students as fetch_students,
    add_marks,
    get_student_marks,
    get_student,
    add_faculty,
    get_faculty,
    get_faculty_member,
    add_course,
    get_courses,
    add_enrollment,
    get_student_enrollments,
)
from app.services.student_service import calculate_gpa


def create_app():
    app = Flask(__name__)
    init_db()

    @app.route("/")
    def home():
        return jsonify({
            "message": "Student Academic Management Platform",
            "status": "running"
        })

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"}), 200

    @app.route("/students", methods=["GET"])
    def list_students():
        return jsonify(fetch_students()), 200

    @app.route("/students", methods=["POST"])
    def create_student():
        data = request.get_json(silent=True) or {}
        student_id = str(data.get("student_id", "")).strip()
        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip()

        if not student_id or not name or not email:
            return jsonify({
                "error": "student_id, name and email are required"
            }), 400

        if "@" not in email or "." not in email.split("@")[-1]:
            return jsonify({"error": "A valid email is required"}), 400

        try:
            save_student(student_id, name, email)
        except sqlite3.IntegrityError:
            return jsonify({
                "error": "Student ID or email already exists"
            }), 409

        return jsonify({
            "student_id": student_id,
            "name": name,
            "email": email
        }), 201

    @app.route("/students/<student_id>/marks", methods=["POST"])
    def create_marks(student_id):
        if not get_student(student_id):
            return jsonify({"error": "Student not found"}), 404

        data = request.get_json(silent=True) or {}
        subject = str(data.get("subject", "")).strip()
        marks = data.get("marks")

        if not subject or marks is None:
            return jsonify({
                "error": "subject and marks are required"
            }), 400

        if isinstance(marks, bool) or not isinstance(marks, (int, float)):
            return jsonify({"error": "Marks must be a number"}), 400

        if not 0 <= marks <= 100:
            return jsonify({
                "error": "Marks must be between 0 and 100"
            }), 400

        try:
            add_marks(student_id, subject, marks)
        except sqlite3.IntegrityError:
            return jsonify({
                "error": "Marks for this subject already exist"
            }), 409

        return jsonify({
            "student_id": student_id,
            "subject": subject,
            "marks": marks
        }), 201

    @app.route("/students/<student_id>/marks", methods=["GET"])
    def list_marks(student_id):
        if not get_student(student_id):
            return jsonify({"error": "Student not found"}), 404
        return jsonify(get_student_marks(student_id)), 200

    @app.route("/students/<student_id>/gpa", methods=["GET"])
    def student_gpa(student_id):
        if not get_student(student_id):
            return jsonify({"error": "Student not found"}), 404

        records = get_student_marks(student_id)
        if not records:
            return jsonify({"error": "No marks available"}), 404

        marks = [record["marks"] for record in records]
        average = round(sum(marks) / len(marks), 2)

        return jsonify({
            "student_id": student_id,
            "subjects": records,
            "average_marks": average,
            "gpa": calculate_gpa(marks),
            "calculation_note": (
                "Simplified demo formula: average marks divided by 10; "
                "not an official university GPA."
            )
        }), 200

    @app.route("/faculty", methods=["GET"])
    def list_faculty():
        return jsonify(get_faculty()), 200

    @app.route("/faculty", methods=["POST"])
    def create_faculty():
        data = request.get_json(silent=True) or {}
        faculty_id = str(data.get("faculty_id", "")).strip()
        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip()

        if not faculty_id or not name or not email:
            return jsonify({
                "error": "faculty_id, name and email are required"
            }), 400

        if "@" not in email or "." not in email.split("@")[-1]:
            return jsonify({"error": "A valid email is required"}), 400

        try:
            add_faculty(faculty_id, name, email)
        except sqlite3.IntegrityError:
            return jsonify({
                "error": "Faculty ID or email already exists"
            }), 409

        return jsonify({
            "faculty_id": faculty_id,
            "name": name,
            "email": email
        }), 201

    @app.route("/courses", methods=["GET"])
    def list_courses():
        return jsonify(get_courses()), 200

    @app.route("/courses", methods=["POST"])
    def create_course():
        data = request.get_json(silent=True) or {}
        course_id = str(data.get("course_id", "")).strip()
        name = str(data.get("name", "")).strip()
        credits = data.get("credits")
        faculty_id = data.get("faculty_id")
        faculty_id = str(faculty_id).strip() if faculty_id else None

        if not course_id or not name or credits is None:
            return jsonify({
                "error": "course_id, name and credits are required"
            }), 400

        if isinstance(credits, bool) or not isinstance(credits, int):
            return jsonify({"error": "Credits must be a whole number"}), 400

        if not 1 <= credits <= 18:
            return jsonify({
                "error": "Course credits must be between 1 and 18"
            }), 400

        if faculty_id and not get_faculty_member(faculty_id):
            return jsonify({"error": "Faculty not found"}), 404

        try:
            add_course(course_id, name, credits, faculty_id)
        except sqlite3.IntegrityError:
            return jsonify({
                "error": (
                    "Course ID already exists or faculty reference is invalid"
                )
            }), 409

        return jsonify({
            "course_id": course_id,
            "name": name,
            "credits": credits,
            "faculty_id": faculty_id
        }), 201

    @app.route("/students/<student_id>/enrollments", methods=["GET"])
    def list_enrollments(student_id):
        if not get_student(student_id):
            return jsonify({"error": "Student not found"}), 404
        return jsonify(get_student_enrollments(student_id)), 200

    @app.route("/enrollments", methods=["POST"])
    def create_enrollment():
        data = request.get_json(silent=True) or {}
        student_id = str(data.get("student_id", "")).strip()
        course_id = str(data.get("course_id", "")).strip()
        semester = str(data.get("semester", "")).strip()

        if not student_id or not course_id or not semester:
            return jsonify({
                "error": "student_id, course_id and semester are required"
            }), 400

        try:
            add_enrollment(student_id, course_id, semester)
        except LookupError as error:
            return jsonify({"error": str(error)}), 404
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        except sqlite3.IntegrityError:
            return jsonify({
                "error": (
                    "Student is already enrolled in this course "
                    "for this semester"
                )
            }), 409

        return jsonify({
            "message": "Enrollment successful",
            "student_id": student_id,
            "course_id": course_id,
            "semester": semester
        }), 201

    return app
