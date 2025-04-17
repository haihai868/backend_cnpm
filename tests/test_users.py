import pytest

from app import security
from app.schemas import UserOut
from tests.test_database_connect import client, db

def test_create_user(client):
    response = client.post('/users/', json={'email': 'test@gmail.com', 'password': 'test', 'fullname': 'test'})
    test_user = UserOut(**response.json())
    assert response.status_code == 201
    assert test_user.email == 'test@gmail.com'
    assert test_user.fullname == 'test'

def test_create_user_failed(client, create_user):
    response = client.post('/users/', json={'email': 'test@gmail.com', 'password': 'test', 'fullname': 'test'})
    assert response.status_code == 400
    assert response.json().get('detail') == 'Email already registered'

def test_login(client, create_user):
    response = client.post('/login', data={'username': create_user['email'], 'password': create_user['password']})
    assert response.status_code == 200
    assert response.json().get('access_token') is not None

@pytest.mark.parametrize('email, password, status_code', [
    ('test@gmail.com', 'test1', 403),
    ('test1@gmail.com', 'test', 403),
    ('test1@gmail.com', 'test1', 403),
    (None, 'test', 403),
    ('test@gmail.com', None, 403)
])
def test_failed_login(email, password, status_code, client, create_user):
    response = client.post('/login', data={'username': email, 'password': password})
    assert response.status_code == status_code
    assert response.json().get('detail') == 'Incorrect email or password'

def test_update_user(authorized_client, create_user):
    response = authorized_client.put('/users/', json={'email': 'test@gmail.com', 'password': 'test1', 'fullname': 'test'})
    assert response.status_code == 200
    assert response.json()['email'] == 'test@gmail.com'
    assert response.json()['fullname'] == 'test'
    assert security.verify('test1', response.json()['password'])
    assert response.json()['id'] == create_user['id']

@pytest.mark.parametrize('password, status_code', [
    ('test1', 403),
    ('test', 200)
])
def test_password_verification(authorized_client, create_user, password, status_code):
    response = authorized_client.post(f'/users/password-verification/{password}')
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json()['message'] == 'Password is correct'
    else:
        assert response.json()['detail'] == 'Incorrect password'

    #full