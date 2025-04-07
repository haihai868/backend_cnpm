import pytest

from tests.test_database_connect import client, db

def test_create_order(client):
    response = client.post('/orders/', json={"user_id": 1, "description": "test"})
    assert response.status_code == 201

    new_order = response.json()
    assert new_order['description'] == "test"
    assert new_order['user_id'] == 1

@pytest.mark.parametrize("product_id, order_id, quantity, status_code", [
    (1, 1, 1, 201),
    (1, 1, -5, 400),
])
def test_add_product_to_order(client, create_order, create_product):
    response = client.put(f'/orders/{id}/', json={"order_id": 1, "product_id": 1, "quantity": 1})
    assert response.status_code == 201
    new_product = response.json()
    assert new_product['quantity'] == 1
    assert new_product['product_id'] == 1
    assert new_product['order_id'] == 1
