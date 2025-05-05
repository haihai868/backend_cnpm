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

@pytest.mark.parametrize('name, status_code', [
    ('test_product', 200),
    ('test_product1', 404)
])
def test_get_product_by_name(client, create_product, name, status_code):
    response = client.get(f'/products/name/{name}')
    assert response.status_code == status_code
    if status_code == 404:
        assert response.json()['detail'] == 'Product not found'
        return
    assert response.json()[0]['name'] == create_product['name']

def test_add_product(client, mock_astradb, create_category):
    response = client.post('/products/', json={'name': 'test_product', 'description': 'test_desc', 'price': 10, 'size': 'S', 'quantity_in_stock': 10, 'category_id': 1, 'age_gender': 'Men'})
    assert response.status_code == 201
    assert response.json()['name'] == 'test_product'
    assert response.json()['description'] == 'test_desc'
    assert response.json()['price'] == 10
    assert response.json()['size'] == 'S'
    print(mock_astradb.documents)
    assert mock_astradb.documents['1'] is not None

@pytest.mark.parametrize('name, description, price, size, quantity_in_stock, category_id, age_gender, status_code', [
    ('test_product', 'test_desc', 10, 'S', 10, 1, 'Men', 400),
    ('test_product', 'test_desc', 10, 'S', 10, 10, 'Men', 404),
    ('test_product', 'test_desc', 10, 'SS', 10, 1, 'Men', 400),
    ('test_product', 'test_desc', 10, 'S', 10, 1, 'Men1', 400),
])
def test_add_product_failed(client, create_product, name, description, price, size, quantity_in_stock, category_id, age_gender, status_code):
    response = client.post('/products/', json={'name': name, 'description': description, 'price': price, 'size': size, 'quantity_in_stock': quantity_in_stock, 'category_id': category_id, 'age_gender': age_gender})
    assert response.status_code == status_code
    if status_code == 400:
        assert response.json()['detail'] == 'Product with this size already exists' or 'Invalid size' or 'Invalid age-gender'
    else:
        assert response.json()['detail'] == 'Category not found'
        return

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

@pytest.mark.parametrize('name, description, price, size, quantity_in_stock, category_id, age_gender, status_code', [
    ('updated_product', 'test_desc', 10, 'S', 10, 1, 'Mens', 400),
    ('test_product', 'test_desc', 10, 'SS', 10, 1, 'Men', 400),
    ('test_product', 'test_desc', 10, 'S', 10, 10, 'Men', 404),
    ('test_product', 'test_desc', 10, 'S', 10, 1, 'Men1', 400),
])
def test_update_product_failed(client, create_product, name, description, price, size, quantity_in_stock, category_id, age_gender, status_code):
    response = client.put(f'/products/{create_product["id"]}', json={'name': name, 'description': description, 'price': price, 'size': size, 'quantity_in_stock': quantity_in_stock, 'category_id': category_id, 'age_gender': age_gender})
    assert response.status_code == status_code
    if status_code == 400:
        assert response.json()['detail'] == 'Product with this size already exists' or 'Invalid size' or 'Invalid age-gender'
    else:
        assert response.json()['detail'] == 'Category not found'
        return

def test_get_products_by_criteria(client, create_products):
    client.post('/products/', json={'name': 'test_product3', 'description': 'test_desc', 'price': 30, 'size': 'S', 'quantity_in_stock': 30, 'category_id': 1, 'age_gender': 'Men'})
    client.post('/products/', json={'name': 'test_product4', 'description': 'test_desc', 'price': 40, 'size': 'S', 'quantity_in_stock': 40, 'category_id': 2, 'age_gender': 'Men'})
    client.post('/products/', json={'name': 'test_product5', 'description': 'test_desc', 'price': 50, 'size': 'S', 'quantity_in_stock': 50, 'category_id': 1, 'age_gender': 'Men'})
    client.post('/products/', json={'name': 'test_product6', 'description': 'test_desc', 'price': 60, 'size': 'S', 'quantity_in_stock': 60, 'category_id': 2, 'age_gender': 'Women'})
    response = client.get('/products/?search=test_product&category=test_category&size=S&priceMin=10&priceMax=60&quantityInStockMin=10&quantityInStockMax=50&ageGender=Men&maxRating=5&minRating=0')
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert response.json()[0][0]['name'] == 'test_product'
    assert response.json()[1][0]['name'] == 'test_product3'
    assert response.json()[2][0]['name'] == 'test_product5'

    response = client.get('/products/?search=test_product&category=test_category&size=S&priceMin=10&priceMax=20&quantityInStockMin=10&quantityInStockMax=20&ageGender=Men&maxRating=5&minRating=0')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0][0]['name'] == 'test_product'

    response = client.get('/products/?search=test_product&category=test_category2&size=S&priceMin=10&priceMax=30&quantityInStockMin=10&quantityInStockMax=20&ageGender=Men&maxRating=5&minRating=0')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0][0]['name'] == 'test_product2'

    response = client.get('/products/?search=test_product&category=test_category2&size=S&priceMin=10&priceMax=50&quantityInStockMin=10&quantityInStockMax=60&ageGender=Men&maxRating=5&minRating=0')
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0][0]['name'] == 'test_product2'
    assert response.json()[1][0]['name'] == 'test_product4'

    response = client.get('/products/?search=test_product&category=test_category2&size=S&priceMin=30&priceMax=60&quantityInStockMin=10&quantityInStockMax=60&ageGender=Women&maxRating=5&minRating=0')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0][0]['name'] == 'test_product6'

    response = client.get('/products/?search=test_product&category=test_category2&size=S&priceMin=10&priceMax=60&quantityInStockMin=10&quantityInStockMax=60&ageGender=Men&maxRating=5&minRating=1')
    assert response.status_code == 200
    assert len(response.json()) == 0

@pytest.mark.parametrize('search, category, size, priceMin, priceMax, quantityInStockMin, quantityInStockMax, ageGender, maxRating, minRating, status_code', [
    ('test_product', 'test_category', 'SS', 10, 60, 10, 10, 'Men', 5, 0, 400),
    ('test_product', 'test_category', 'S', 10, 60, 10, 10, 'Men1', 5, 0, 400),
])
def test_get_products_by_criteria_failed(client, create_products, search, category, size, priceMin, priceMax, quantityInStockMin, quantityInStockMax, ageGender, maxRating, minRating, status_code):
    response = client.get(f'/products/?search={search}&category={category}&size={size}&priceMin={priceMin}&priceMax={priceMax}&quantityInStockMin={quantityInStockMin}&quantityInStockMax={quantityInStockMax}&ageGender={ageGender}&maxRating={maxRating}&minRating={minRating}')
    assert response.status_code == status_code
    assert response.json()['detail'] == 'Invalid size' or 'Invalid age-gender'

def test_get_avg_rating(client, create_product, create_reviews_for_1_product):
    response = client.get(f'/products/avg_rating/{create_product["id"]}')
    assert response.status_code == 200
    assert response.json()['product_id'] == create_product['id']
    assert response.json()['avg_rating'] == 3.0

def test_get_favourites_by_user_id(authorized_client, create_favourites):
    response = authorized_client.get(f'/products/user/favourites/1')
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['id'] == create_favourites[0]['id']
    assert response.json()[0]['name'] == create_favourites[0]['name']
    assert response.json()[0]['description'] == create_favourites[0]['description']
    assert response.json()[0]['size'] == create_favourites[0]['size']

    assert response.json()[1]['id'] == create_favourites[1]['id']
    assert response.json()[1]['name'] == create_favourites[1]['name']
    assert response.json()[1]['description'] == create_favourites[1]['description']
    assert response.json()[1]['size'] == create_favourites[1]['size']

def test_add_favourite(authorized_client, create_product):
    response = authorized_client.post(f'/products/user/favourite/{create_product["id"]}')
    assert response.status_code == 201
    assert response.json()['id'] == create_product['id']
    assert response.json()['name'] == create_product['name']
    assert response.json()['description'] == create_product['description']

def test_delete_favourite(authorized_client, create_favourites):
    response = authorized_client.delete(f'/products/favourite/{create_favourites[0]["id"]}')
    assert response.status_code == 200
    assert response.json()['message'] == 'Favourite deleted successfully'

    response = authorized_client.delete(f'/products/favourite/{create_favourites[1]["id"]}')
    assert response.status_code == 200
    assert response.json()['message'] == 'Favourite deleted successfully'

    response = authorized_client.get(f'products/user/favourites/1')
    assert response.status_code == 200
    assert len(response.json()) == 0