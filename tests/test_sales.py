from tests.test_database_connect import client, db

def test_create_sale(authorized_admin_client, create_products):
    response = authorized_admin_client.post('/sales/', json={'discount_percentage': 10, 'age_gender': 'Men', 'category_id': 1})

    print(response.json())
    assert response.status_code == 201
    assert response.json()['discount_percentage'] == 10
    assert response.json()['age_gender'] == 'Men'
    assert response.json()['category_id'] == 1

    products = authorized_admin_client.get('/products').json()
    assert products[0][0]['price'] == 9
    assert products[0][0]['old_price'] == 10

    assert products[1][0]['price'] == 20

    response = authorized_admin_client.post('/sales/', json={'discount_percentage': 10, 'age_gender': 'Men'})
    assert response.status_code == 201
    assert response.json()['discount_percentage'] == 10
    assert response.json()['age_gender'] == 'Men'

    products = authorized_admin_client.get('/products').json()
    assert products[0][0]['price'] == 8
    assert products[0][0]['old_price'] == 10

    assert products[1][0]['price'] == 18
    assert products[1][0]['old_price'] == 20

def test_create_sale_failed(authorized_admin_client, create_products):
    response = authorized_admin_client.post('/sales/', json={'discount_percentage': 110, 'age_gender': 'Men', 'category_id': 1})

    assert response.status_code == 400
    assert response.json()['detail'] == 'Invalid discount percentage'

def test_end_sale(authorized_admin_client, create_products):
    response = authorized_admin_client.post('/sales/', json={'discount_percentage': 10, 'age_gender': 'Men'})
    response1 = authorized_admin_client.post('/sales/', json={'discount_percentage': 10, 'age_gender': 'Men', 'category_id': 1})
    assert response.status_code == 201
    assert response1.status_code == 201

    response = authorized_admin_client.put(f'/sales/{response.json()["id"]}')
    assert response.status_code == 200
    assert response.json()['end_date'] is not None

    products = authorized_admin_client.get('/products').json()
    assert products[0][0]['price'] == 9
    assert products[0][0]['old_price'] == 10

    response1 = authorized_admin_client.put(f'/sales/{response1.json()["id"]}')
    assert response1.status_code == 200
    assert response1.json()['end_date'] is not None

    products = authorized_admin_client.get('/products').json()
    assert products[0][0]['price'] == 10
    assert products[0][0]['old_price'] is None

    assert products[1][0]['price'] == 20
    assert products[1][0]['old_price'] is None

