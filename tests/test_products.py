import pytest

from tests.test_database_connect import client, db

@pytest.mark.parametrize('id, status_code', [
    (1, 200),
    (3, 404)
])
def test_get_product_by_id(client, create_product, id, status_code):
    response = client.get(f'/products/{id}')
    assert response.status_code == status_code
    if status_code == 404:
        assert response.json()['detail'] == 'Product not found'
        return
    assert response.json()['id'] == create_product['id']
    assert response.json()['name'] == create_product['name']
    assert response.json()['description'] == create_product['description']
    assert response.json()['size'] == create_product['size']

def test_get_product_by_name(client, create_product):
    response = client.get(f'/products/name/{create_product["name"]}')
    assert response.status_code == 200
    assert response.json()[0]['name'] == create_product['name']

@pytest.mark.parametrize('name, description, price, size, quantity_in_stock, category_id, age_gender', [
    ('updated_product', 'test_desc', 10, 'S', 10, 1, 'Men'),
    ('test_product', 'updated_desc', 10, 'S', 10, 1, 'Men'),
    ('test_product', 'test_desc', 15, 'S', 10, 1, 'Men'),
    ('test_product', 'test_desc', 10, 'M', 10, 1, 'Men'),
    ('test_product', 'test_desc', 10, 'S', 100, 1, 'Men'),
    ('test_product', 'test_desc', 10, 'S', 100, 1, 'Kids'),
])
def test_update_product(name, description, price, size, quantity_in_stock, category_id, age_gender, client, create_product):
    response = client.put(f'/products/{create_product["id"]}', json={'name': name, 'description': description, 'price': price, 'size': size, 'quantity_in_stock': quantity_in_stock, 'category_id': category_id, 'age_gender': age_gender})
    assert response.status_code == 200
    assert response.json()['name'] == name
    assert response.json()['description'] == description
    assert response.json()['price'] == price
    assert response.json()['size'] == size
    assert response.json()['quantity_in_stock'] == quantity_in_stock
    assert response.json()['category_id'] == category_id
    assert response.json()['age_gender'] == age_gender

