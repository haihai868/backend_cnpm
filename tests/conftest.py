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
def create_user2(client):
    res = client.post("/users/", json={"email": "test2@gmail.com", 'fullname': 'test2',"password": "test2"})

    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = "test2"
    return new_user

@pytest.fixture
def create_admin(client):
    res = client.post("/admins/", json={"email": "test@gmail.com", "password": "test"})

    assert res.status_code == 201

    new_admin = res.json()
    new_admin['password'] = "test"
    return new_admin

@pytest.fixture
def authorized_client(client, create_user):
    token = create_access_token({"user_email": create_user['email'], "user_id": create_user['id']})
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture
def authorized_admin_client(client, create_admin):
    token = create_access_token({"user_email": create_admin['email'], "user_id": create_admin['id']})
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
    response1 = client.post("/products/", json={"name": "test_product2", "description": "test_desc", "price": 20, "size": "S", "quantity_in_stock": 20, "category_id": 2, "age_gender": "Men"})

    assert response.status_code == 201
    assert response1.status_code == 201

    new_products = response.json(), response1.json()
    return new_products

@pytest.fixture
def create_reviews_for_1_product(authorized_client, create_user2, create_product):
    response = authorized_client.post('/reviews/', json={'rating': '1', 'comment': 'test', 'product_id': create_product['id']})
    assert response.status_code == 201

    authorized_client.headers.update({'Authorization': f'Bearer {create_access_token({"user_email": create_user2["email"], "user_id": create_user2["id"]})}'})
    response1 = authorized_client.post('/reviews/', json={'rating': '5', 'comment': 'test2', 'product_id': create_product['id']})
    assert response.status_code == 201
    assert response1.status_code == 201
    assert response.json()['product_id'] == create_product['id']
    return response.json(), response1.json()

@pytest.fixture
def create_reviews_for_1_user(authorized_client, create_products):
    response = authorized_client.post('/reviews/', json={'rating': '1', 'comment': 'test', 'product_id': create_products[0]['id']})
    assert response.status_code == 201

    response1 = authorized_client.post('/reviews/', json={'rating': '5', 'comment': 'test2', 'product_id': create_products[1]['id']})
    assert response1.status_code == 201
    return response.json(), response1.json()

@pytest.fixture
def create_order(client, create_user):
    response = client.post('/orders/', json={"user_id": create_user['id'], "description": "test"})
    assert response.status_code == 201
    return response.json()

@pytest.fixture
def create_orders(client, create_user):
    response = client.post('/orders/', json={"user_id": create_user['id'], "description": "test"})
    response1 = client.post('/orders/', json={"user_id": create_user['id'], "description": "test"})
    assert response.status_code == 201
    assert response1.status_code == 201
    return response.json(), response1.json()

@pytest.fixture
def create_notifications(client, create_user, create_user2):
    response = client.post('/notifications/', json={'user_id': create_user["id"], 'title': 'test', 'message': 'test'})
    response1 = client.post('/notifications/', json={'user_id': create_user["id"], 'title': 'test2', 'message': 'test2'})
    response2 = client.post('/notifications/', json={'user_id': create_user2["id"], 'title': 'test3', 'message': 'test3'})

    assert response.status_code == 201
    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response.json()['is_read'] == False

    return response.json(), response1.json(), response2.json()

@pytest.fixture
def create_favourites(client, create_user, create_products):
    response = client.post('/products/user/favourite/1')
    assert response.status_code == 201
    response1 = client.post('/products/user/favourite/2')
    assert response1.status_code == 201
    return response.json(), response1.json()

@pytest.fixture
def pay_order(authorized_client, create_order, create_products):
    authorized_client.put('/orders/product', json={"product_id": create_products[0]['id'], "quantity": 8})
    authorized_client.put('/orders/product', json={"product_id": create_products[1]['id'], "quantity": 1})
    response = authorized_client.put('/orders/payment')
    return response.json()

@pytest.fixture
def create_report(authorized_client, create_user2, create_product):
    response = authorized_client.post('/reports/', json={'message': 'test', 'product_id': create_product['id']})
    assert response.status_code == 201
    return response.json()