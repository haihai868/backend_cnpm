import pytest

from app import security
from app.schemas import AdminOut
from tests.test_database_connect import client, db

def test_create_admin(client):
    response = client.post('/admins/', json={'email': 'test@gmail.com', 'password': 'test'})
    assert response.status_code == 201
    assert response.json()['email'] == 'test@gmail.com'
    assert response.json()['id'] == 1
    assert response.json()['password'] != 'test'

def test_create_admin_failed(client, create_admin):
    response = client.post('/admins/', json={'email': 'test@gmail.com', 'password': 'test'})
    assert response.status_code == 400
    assert response.json()['detail'] == 'Email already registered'

def test_login(client, create_admin):
    response = client.post('/admin-login', data={'username': create_admin['email'], 'password': create_admin['password']})
    assert response.status_code == 200
    assert response.json()['access_token'] is not None

@pytest.mark.parametrize('email, password, status_code', [
    ('test@gmail.com', 'test1', 403),
    ('test1@gmail.com', 'test', 403),
    ('test1@gmail.com', 'test1', 403),
    (None, 'test', 403),
    ('test@gmail.com', None, 403)
])
def test_failed_login(client, create_admin, email, password, status_code):
    response = client.post('/admin-login', data={'username': email, 'password': password})
    assert response.status_code == status_code
    assert response.json()['detail'] == 'Incorrect username or password'

def test_update_admin(authorized_admin_client, create_admin):
    response = authorized_admin_client.put('/admins/', json={'email': 'test@gmail.com', 'password': 'test1'})
    assert response.status_code == 200
    assert response.json()['email'] == 'test@gmail.com'
    assert security.verify('test1', response.json()['password'])
    assert response.json()['id'] == create_admin['id']
    assert response.json()['password'] != 'test'

@pytest.mark.parametrize('password, status_code', [
    ('test1', 403),
    ('test', 200)
])
def test_password_verification(authorized_admin_client, create_admin, password, status_code):
    response = authorized_admin_client.post(f'/admins/password-verification/{password}')
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json()['message'] == 'Password is correct'
    else:
        assert response.json()['detail'] == 'Incorrect password'
