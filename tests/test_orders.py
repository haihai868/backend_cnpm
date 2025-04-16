import pytest

from tests.conftest import authorized_client
from tests.test_database_connect import client, db

def test_create_order(client):
    response = client.post('/orders/', json={"user_id": 1, "description": "test"})
    assert response.status_code == 201

    new_order = response.json()
    assert new_order['description'] == "test"
    assert new_order['user_id'] == 1

def test_create_order_failed(client, create_order):
    response = client.post('/orders/', json={"user_id": 1, "description": "test"})
    assert response.status_code == 400
    assert response.json()['detail'] == 'User already has an unpaid order'

def test_update_order(authorized_client, create_order):
    response = authorized_client.put('/orders/', json={"user_id": 1, "description": "test2"})
    assert response.status_code == 200
    assert response.json()['description'] == "test2"
    assert response.json()['user_id'] == 1

def test_get_products_in_order_by_id(authorized_client, create_order, create_products):
    authorized_client.put('/orders/product', json={"product_id": create_products[0]['id'], "quantity": 1})
    authorized_client.put('/orders/product', json={"product_id": create_products[1]['id'], "quantity": 1})
    response = authorized_client.get(f'/orders/{create_order["id"]}/products')
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['id'] == create_products[0]['id']
    assert response.json()[1]['id'] == create_products[1]['id']

@pytest.mark.parametrize("quantity, price_each, status_code", [
    (1, None, 200),
    (0, 100, 400),
    (1, 10, 200)
])
def test_add_product_to_order(authorized_client, create_order, create_product, quantity, price_each, status_code):
    response = authorized_client.put('/orders/product', json={"product_id": create_product['id'], "quantity": quantity})
    assert response.status_code == status_code
    if status_code == 400:
        return
    new_order_detail = response.json()
    assert new_order_detail['product_id'] == create_product['id']
    assert new_order_detail['quantity'] == quantity
    assert new_order_detail['priceEach'] == price_each or create_product['price']
    assert new_order_detail['order_id'] == create_order['id']

@pytest.mark.parametrize("status", [
    'Paid',
    'All',
    'Unpaid'
])
def test_get_orders_by_user_id(client, create_order, status):
    pass

def test_delete_product_from_order(authorized_client, create_order, create_product):
    authorized_client.put('/orders/product', json={"product_id": create_product['id'], "quantity": 1})
    response = authorized_client.delete(f'/orders/{create_order["id"]}')
    assert response.status_code == 200
    assert response.json() == {'message': 'Product deleted successfully'}

def test_delete_product_from_order_failed(authorized_client, create_order, create_product):
    response = authorized_client.delete(f'/orders/10')
    assert response.status_code == 404
    assert response.json()['detail'] == "Product not in user's order"

def test_get_products_in_order(authorized_client, create_order, create_products):
    authorized_client.put('/orders/product', json={"product_id": create_products[0]['id'], "quantity": 1})
    authorized_client.put('/orders/product', json={"product_id": create_products[1]['id'], "quantity": 1})
    response = authorized_client.get('/orders/products/')
    assert response.status_code == 200
    print(response.json())
    assert len(response.json()) == 2
    assert response.json()[0]['id'] == create_products[0]['id']
    assert response.json()[1]['id'] == create_products[1]['id']

def test_get_total_order_price(authorized_client, create_order, create_products):
    authorized_client.put('/orders/product', json={"product_id": create_products[0]['id'], "quantity": 1})
    authorized_client.put('/orders/product', json={"product_id": create_products[1]['id'], "quantity": 1})
    response = authorized_client.get(f'/orders/{create_order["id"]}/total_price')
    assert response.status_code == 200
    assert response.json()['total'] == 20
    assert response.json()['order_id'] == create_order['id']


