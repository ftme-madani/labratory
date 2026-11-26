import pytest
from fastapi.testclient import TestClient

def test_register_student_success(client: TestClient):
    payload = {
        "username": "new_student",
        "email": "new_student@school.ir",
        "password": "Password123!",
        "full_name": "سارا حسینی",
        "role": "student",
        "grade": "نهم",
        "school_name": "دبیرستان فرزانگان"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "new_student"
    assert data["user"]["email"] == "new_student@school.ir"
    assert data["user"]["role"] == "student"

def test_register_duplicate_email(client: TestClient, sample_student):
    payload = {
        "username": "another_user",
        "email": sample_student.email,  # duplicate email
        "password": "Password123!",
        "full_name": "کاربر تکراری",
        "role": "student"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "ایمیل" in response.json()["detail"]

def test_register_duplicate_username(client: TestClient, sample_student):
    payload = {
        "username": sample_student.username,  # duplicate username
        "email": "unique_email@test.ir",
        "password": "Password123!",
        "full_name": "کاربر تکراری ۲",
        "role": "student"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "نام کاربری" in response.json()["detail"]

def test_login_success(client: TestClient, sample_student):
    payload = {
        "email": sample_student.email,
        "password": "SecretPass123"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == sample_student.email

def test_login_wrong_password(client: TestClient, sample_student):
    payload = {
        "email": sample_student.email,
        "password": "WrongPassword!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "نادرست" in response.json()["detail"]

def test_get_current_user_profile(client: TestClient, student_auth_headers, sample_student):
    response = client.get("/api/v1/auth/me", headers=student_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_student.email
    assert data["full_name"] == sample_student.full_name

def test_get_current_user_profile_unauthorized(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
