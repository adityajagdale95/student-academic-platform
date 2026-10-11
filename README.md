# Student Academic Management Platform

## Project Overview

The Student Academic Management Platform is a Python Flask web application designed to manage student academic records. It provides REST API endpoints for checking application health and adding and retrieving student records.

## Technologies Used

- Python 3.11
- Flask
- Pytest
- Gunicorn
- Flake8
- Git
- Docker
- Jenkins

## Current Features

- Application home endpoint
- Health check endpoint
- Retrieve student records
- Add new student records
- Validate required student fields
- Prevent duplicate student IDs
- Automated application tests
- Docker container deployment

## Project Structure

```text
student-academic-platform/
├── app/
├── database/
├── tests/
│   └── test_app.py
├── k8s/
├── Dockerfile
├── Jenkinsfile
├── requirements.txt
├── run.py
├── .dockerignore
└── .gitignore
```

## Run Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the application

```bash
python run.py
```

The application runs on port 5000.

### 3. Check application health

```bash
curl http://127.0.0.1:5000/health
```

Expected response:

```json
{"status": "healthy"}
```

## Run Automated Tests

```bash
pytest -v
```

## Run with Docker

Build the image:

```bash
docker build -t student-academic-platform:v1.0.0 .
```

Start a container:

```bash
docker run -d --name student-academic-container -p 5001:5000 student-academic-platform:v1.0.0
```

Check container health:

```bash
curl http://127.0.0.1:5001/health
```

## Current Testing Status

The initial application test suite contains six tests covering the home endpoint, health check, student retrieval, student creation, missing required fields, and duplicate student IDs.

## Future Enhancements

- Persistent database integration
- Faculty and course management
- Enrollment and grade management
- Academic credit limit validation
- Kubernetes deployment
- Jenkins continuous integration

## Note

Student records are currently stored in application memory. They are not persisted to a database, and restarting the application clears them. Additional academic management features remain to be implemented.
