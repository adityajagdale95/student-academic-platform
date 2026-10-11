from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    students = []

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
    def get_students():
        return jsonify(students), 200

    @app.route("/students", methods=["POST"])
    def add_student():
        from flask import request

        data = request.get_json(silent=True) or {}

        student_id = str(data.get("student_id", "")).strip()
        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip()

        if not student_id or not name or not email:
            return jsonify({
                "error": "student_id, name and email are required"
            }), 400

        if any(s["student_id"] == student_id for s in students):
            return jsonify({"error": "Student already exists"}), 409

        student = {
            "student_id": student_id,
            "name": name,
            "email": email
        }

        students.append(student)
        return jsonify(student), 201

    return app
