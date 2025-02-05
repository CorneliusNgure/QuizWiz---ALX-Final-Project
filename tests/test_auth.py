import uuid

def test_register(client):
    """Test user registration"""
    unique_email = f"{uuid.uuid4()}@example2.com"  
    print(f"Testing with email: {unique_email}")  # Debugging line
    response = client.post("/register", data={
        "username": "testuser2",
        "email": unique_email,
        "password": "password123"
    }, follow_redirects=True)

    print(response.data)  # Debugging: Print response data

    assert response.status_code == 200
    assert b"Registration successful! Please log in." in response.data

def test_register_existing_user(client):
    """Test registering with an existing email/username"""
    client.post("/register", data={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    }, follow_redirects=True)

    response = client.post("/register", data={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Username or Email already exists" in response.data


def test_sign_in(client):
    """Test successful login"""
    client.post("/register", data={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    }, follow_redirects=True)

    response = client.post("/sign_in", data={
        "email": "testuser@example.com",
        "password": "password123"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Login successful!" in response.data


def test_sign_in_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post("/sign_in", data={
        "email": "wrong@example.com",
        "password": "wrongpassword"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_logout(client):
    """Test logout"""
    client.post("/register", data={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    }, follow_redirects=True)

    client.post("/sign_in", data={
        "email": "testuser@example.com",
        "password": "password123"
    }, follow_redirects=True)

    response = client.get("/logout", follow_redirects=True)

    assert response.status_code == 200
    assert b"You have been logged out." in response.data


def test_trivia_arena_requires_login(client):
    """Ensure trivia arena requires login"""
    response = client.get("/play", follow_redirects=True)

    assert response.status_code == 200
    assert b"Please log in to play." in response.data
