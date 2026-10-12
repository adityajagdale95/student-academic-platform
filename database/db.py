import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "students.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS marks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                marks REAL NOT NULL CHECK (marks >= 0 AND marks <= 100),
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                UNIQUE (student_id, subject)
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS faculty (
                faculty_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                credits INTEGER NOT NULL CHECK (credits BETWEEN 1 AND 18),
                faculty_id TEXT,
                FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_id TEXT NOT NULL,
                semester TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (course_id) REFERENCES courses(course_id),
                UNIQUE (student_id, course_id, semester)
            )
        """)


def add_student(student_id, name, email):
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO students VALUES (?, ?, ?)",
            (student_id, name, email)
        )


def get_students():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT student_id, name, email FROM students ORDER BY student_id"
        ).fetchall()
        return [dict(row) for row in rows]


def get_student(student_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT student_id, name, email FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()
        return dict(row) if row else None


def add_marks(student_id, subject, marks):
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO marks (student_id, subject, marks) VALUES (?, ?, ?)",
            (student_id, subject, marks)
        )


def get_student_marks(student_id):
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT subject, marks FROM marks WHERE student_id = ? ORDER BY subject",
            (student_id,)
        ).fetchall()
        return [dict(row) for row in rows]


def add_faculty(faculty_id, name, email):
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO faculty VALUES (?, ?, ?)",
            (faculty_id, name, email)
        )


def get_faculty():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT faculty_id, name, email FROM faculty ORDER BY faculty_id"
        ).fetchall()
        return [dict(row) for row in rows]


def get_faculty_member(faculty_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT faculty_id, name, email FROM faculty WHERE faculty_id = ?",
            (faculty_id,)
        ).fetchone()
        return dict(row) if row else None


def add_course(course_id, name, credits, faculty_id=None):
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO courses (course_id, name, credits, faculty_id) "
            "VALUES (?, ?, ?, ?)",
            (course_id, name, credits, faculty_id)
        )


def get_courses():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT c.course_id, c.name, c.credits, c.faculty_id,
                   f.name AS faculty_name
            FROM courses c
            LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
            ORDER BY c.course_id
        """).fetchall()
        return [dict(row) for row in rows]


def get_course(course_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT course_id, name, credits, faculty_id "
            "FROM courses WHERE course_id = ?",
            (course_id,)
        ).fetchone()
        return dict(row) if row else None


def add_enrollment(student_id, course_id, semester):
    with get_connection() as connection:
        student = connection.execute(
            "SELECT student_id FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()
        course = connection.execute(
            "SELECT credits FROM courses WHERE course_id = ?",
            (course_id,)
        ).fetchone()

        if not student:
            raise LookupError("Student not found")
        if not course:
            raise LookupError("Course not found")

        duplicate = connection.execute(
            "SELECT 1 FROM enrollments "
            "WHERE student_id = ? AND course_id = ? AND semester = ?",
            (student_id, course_id, semester)
        ).fetchone()

        if duplicate:
            raise sqlite3.IntegrityError(
                "Student is already enrolled in this course for this semester"
            )

        current = connection.execute("""
            SELECT COALESCE(SUM(c.credits), 0) AS total
            FROM enrollments e
            JOIN courses c ON c.course_id = e.course_id
            WHERE e.student_id = ? AND e.semester = ?
        """, (student_id, semester)).fetchone()["total"]

        if current + course["credits"] > 18:
            raise ValueError(
                f"Credit limit exceeded: current {current}, "
                f"course {course['credits']}, maximum 18 per semester"
            )

        connection.execute(
            "INSERT INTO enrollments (student_id, course_id, semester) "
            "VALUES (?, ?, ?)",
            (student_id, course_id, semester)
        )


def get_student_enrollments(student_id):
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT e.semester, c.course_id, c.name AS course_name, c.credits
            FROM enrollments e
            JOIN courses c ON c.course_id = e.course_id
            WHERE e.student_id = ?
            ORDER BY e.semester, c.course_id
        """, (student_id,)).fetchall()
        return [dict(row) for row in rows]
