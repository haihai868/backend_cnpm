import pytest

from app.security import create_access_token


@pytest.fixture
def create_user(client):
    res = client.post("/users/", json={"email": "test@gmail.com", 'fullname': 'test',"password": "test"})

    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = "test"
    return new_user

@pytest.fixture
def token(create_user):
    return create_access_token({"user_email": create_user['email'], "user_id": create_user['id']})

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture
def create_category(client, create_user):
    res = client.post("/categories/", json={"name": "test_category", "description": "test_desc"})

    assert res.status_code == 201

    new_category = res.json()
    return new_category

@pytest.fixture
def create_categories(client, create_user):
    response = client.post("/categories/", json={"name": "test_category", "description": "test_desc"})
    response1 = client.post("/categories/", json={"name": "test_category2", "description": "test_desc"})

    assert response.status_code == 201
    assert response1.status_code == 201

    new_categories = response.json(), response1.json()
    return new_categories

@pytest.fixture
def create_product(client, create_user, create_category):
    res = client.post("/products/", json={"name": "test_product", "description": "test_desc", "price": 10, "size": "S", "quantity_in_stock": 10, "category_id": 1, "age_gender": "Men"})
    assert res.status_code == 201

    new_product = res.json()
    return new_product

@pytest.fixture
def create_products(client, create_user, create_categories):
    response = client.post("/products/", json={"name": "test_product", "description": "test_desc", "price": 10, "size": "S", "quantity_in_stock": 10, "category_id": 1, "age_gender": "Men"})
    response1 = client.post("/products/", json={"name": "test_product2", "description": "test_desc", "price": 10, "size": "S", "quantity_in_stock": 10, "category_id": 2, "age_gender": "Men"})

    assert response.status_code == 201
    assert response1.status_code == 201

    new_products = response.json(), response1.json()
    return new_products

@pytest.fixture
def create_order(client, create_user):
    response = client.post('/orders/', json={"user_id": 1, "description": "test"})
    assert response.status_code == 201
    return response.json()