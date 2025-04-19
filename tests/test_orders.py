import pytest

from tests.conftest import authorized_client
from tests.test_database_connect import client, db

def test_get_products_in_order(authorized_client, create_order, create_products):
    authorized_client.put('/orders/product', json={"product_id": create_products[0]['id'], "quantity": 1})
    authorized_client.put('/orders/product', json={"product_id": create_products[1]['id'], "quantity": 1})
    response = authorized_client.get('/orders/products/')
    assert response.status_code == 200
    print(response.json())
    assert len(response.json()) == 2
    assert response.json()[0]['id'] == create_products[0]['id']
    assert response.json()[1]['id'] == create_products[1]['id']
    assert response.json()[0]['quantity_in_order'] == 1
    assert response.json()[1]['quantity_in_order'] == 1

def test_get_products_in_order_by_id(authorized_client, create_order, create_products):
    authorized_client.put('/orders/product', json={"product_id": create_products[0]['id'], "quantity": 1})
    authorized_client.put('/orders/product', json={"product_id": create_products[1]['id'], "quantity": 1})
    response = authorized_client.get(f'/orders/{create_order["id"]}/products')
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['id'] == create_products[0]['id']
    assert response.json()[1]['id'] == create_products[1]['id']

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

def test_delete_product_from_order(authorized_client, create_order, create_product):
    authorized_client.put('/orders/product', json={"product_id": create_product['id'], "quantity": 1})
    response = authorized_client.delete(f'/orders/{create_order["id"]}')
    assert response.status_code == 200
    assert response.json() == {'message': 'Product deleted successfully'}

@pytest.mark.parametrize("status", [
    'Paid',
    'All',
    'Unpaid'
])
def test_get_orders_by_user_id(client, create_order, status):
    response = client.get(f'/orders/users/1?status={status}')
    assert response.status_code == 200
    if status == 'Paid':
        assert len(response.json()) == 0
        return
    assert len(response.json()) == 1
    assert response.json()[0]['id'] == create_order['id']
    assert response.json()[0]['user_id'] == create_order['user_id']
    assert response.json()[0]['description'] == create_order['description']
    assert response.json()[0]['status'] == create_order['status']
    assert response.json()[0]['created_at'] == create_order['created_at']

def test_delete_product_from_order_failed(authorized_client, create_order, create_product):
    response = authorized_client.delete(f'/orders/10')
    assert response.status_code == 404
    assert response.json()['detail'] == "Product not in user's order"
    response = authorized_client.delete(f'/orders/{create_order["id"]}')
    assert response.status_code == 404
    assert response.json()['detail'] == "Product not in user's order"

def test_get_total_order_price(authorized_client, create_order, create_products):
    authorized_client.put('/orders/product', json={"product_id": create_products[0]['id'], "quantity": 1})
    authorized_client.put('/orders/product', json={"product_id": create_products[1]['id'], "quantity": 1})
    response = authorized_client.get(f'/orders/{create_order["id"]}/total_price')
    assert response.status_code == 200
    assert response.json()['total'] == 30
    assert response.json()['order_id'] == create_order['id']

def test_pay_order(authorized_client, create_order, create_products):
    authorized_client.put('/orders/product', json={"product_id": create_products[0]['id'], "quantity": 8})
    authorized_client.put('/orders/product', json={"product_id": create_products[1]['id'], "quantity": 1})
    response = authorized_client.put('/orders/payment')
    assert response.status_code == 200
    assert response.json()['status'] == 'Pending'
    assert response.json()['id'] == create_order['id']
    assert response.json()['user_id'] == create_order['user_id']
    assert response.json()['description'] == create_order['description']
    assert response.json()['created_at'] == create_order['created_at']
    assert response.json()['status'] == 'Pending'

    products = authorized_client.get('/products').json()
    assert products[0][0]['quantity_in_stock'] == 2
    assert products[1][0]['quantity_in_stock'] == 19

def test_pay_order_failed(authorized_client, create_order, create_products):
    authorized_client.put('/orders/product', json={"product_id": create_products[0]['id'], "quantity": 11})
    authorized_client.put('/orders/product', json={"product_id": create_products[1]['id'], "quantity": 1})
    response = authorized_client.put('/orders/payment')

    assert response.status_code == 400
    assert response.json()['detail'] == f'Not enough product {create_products[0]["name"]} in stock'
    response = authorized_client.get('/orders/1').json()
    assert response['status'] == 'Unpaid'

def test_confirm_payment(authorized_admin_client, pay_order, create_products):
    response = authorized_admin_client.put(f'/orders/payment/confirmation/{pay_order["id"]}')
    assert response.status_code == 200
    assert response.json()['status'] == 'Paid'
    assert response.json()['id'] == pay_order['id']
    assert response.json()['user_id'] == pay_order['user_id']
    assert response.json()['description'] == pay_order['description']
    assert response.json()['created_at'] == pay_order['created_at']

def test_cancel_payment(authorized_client, pay_order, create_products):
    response = authorized_client.delete(f'/orders/payment/cancelation/{pay_order["id"]}')
    assert response.status_code == 200
    assert response.json()['message'] == 'Order canceled successfully'

    products = authorized_client.get('/products').json()
    assert products[0][0]['quantity_in_stock'] == 10
    assert products[1][0]['quantity_in_stock'] == 20

def test_cancel_payment_failed(authorized_client, create_order, create_products):
    response = authorized_client.delete(f'/orders/payment/cancelation/{create_order["id"]}')
    assert response.status_code == 400
    assert response.json()['detail'] == 'Order is not pending'

def test_admin_cancel_payment(authorized_admin_client, pay_order, create_products):
    response = authorized_admin_client.delete(f'/orders/payment/admin/cancelation/{pay_order["id"]}')
    assert response.status_code == 200
    assert response.json()['message'] == 'Order canceled successfully'
    products = authorized_admin_client.get('/products').json()
    assert products[0][0]['quantity_in_stock'] == 10
    assert products[1][0]['quantity_in_stock'] == 20
