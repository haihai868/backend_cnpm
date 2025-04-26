import pytest

from tests.test_database_connect import db, client

def test_create_review(authorized_client, create_product):
    response = authorized_client.post('/reviews/', json={'rating': '1', 'comment': 'test', 'product_id': create_product['id']})
    assert response.status_code == 201
    assert response.json()['rating'] == '1'
    assert response.json()['comment'] == 'test'
    assert response.json()['product_id'] == create_product['id']

@pytest.mark.parametrize('rating, comment, product_id, status_code', [
    ('1', 'test', 10, 404),
    ('1', 'test', 1, 403)
])
def test_create_review_failed(authorized_client, create_product, create_reviews_for_1_product, rating, comment, product_id, status_code):
    response = authorized_client.post('/reviews/', json={'rating': rating, 'comment': comment, 'product_id': product_id})
    assert response.status_code == status_code
    if status_code == 404:
        assert response.json()['detail'] == 'Product not found'
    else:
        assert response.json()['detail'] == 'You have already reviewed this product'

def test_get_review(authorized_client, create_product):
    response = authorized_client.post('/reviews/', json={'rating': '1', 'comment': 'test', 'product_id': create_product['id']})
    assert response.status_code == 201
    response = authorized_client.get(f'/reviews/{response.json()["id"]}')
    res = response.json()
    assert response.status_code == 200
    assert res['rating'] == '1'
    assert res['comment'] == 'test'
    assert res['product_id'] == create_product['id']

def test_get_reviews_by_product_id(authorized_client, create_reviews_for_1_product):
    response = authorized_client.get(f'/reviews/products/{create_reviews_for_1_product[0]["product_id"]}')
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['rating'] == create_reviews_for_1_product[0]['rating']
    assert response.json()[0]['comment'] == create_reviews_for_1_product[0]['comment']
    assert response.json()[0]['product_id'] == create_reviews_for_1_product[0]['product_id']
    assert response.json()[0]['user_id'] == 1

    assert response.json()[1]['rating'] == create_reviews_for_1_product[1]['rating']
    assert response.json()[1]['comment'] == create_reviews_for_1_product[1]['comment']
    assert response.json()[1]['product_id'] == create_reviews_for_1_product[1]['product_id']
    assert response.json()[1]['user_id'] == 2

def test_get_reviews_by_user_id(client, create_reviews_for_1_user):
    response = client.get(f'/reviews/users/1')
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['rating'] == create_reviews_for_1_user[0]['rating']
    assert response.json()[0]['comment'] == create_reviews_for_1_user[0]['comment']
    assert response.json()[0]['product_id'] == create_reviews_for_1_user[0]['product_id']

    assert response.json()[1]['rating'] == create_reviews_for_1_user[1]['rating']
    assert response.json()[1]['comment'] == create_reviews_for_1_user[1]['comment']
    assert response.json()[1]['product_id'] == create_reviews_for_1_user[1]['product_id']

def test_delete_review(authorized_client, create_product):
    response = authorized_client.post('/reviews/', json={'rating': '1', 'comment': 'test', 'product_id': 1})
    assert response.status_code == 201
    del_res = authorized_client.delete(f'/reviews/{response.json()["id"]}')
    assert del_res.status_code == 200
    assert del_res.json()['message'] == 'Review deleted successfully'

    response = authorized_client.get(f'/reviews/{response.json()["id"]}')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Review not found'

def test_admin_delete_user_reviews(authorized_admin_client, create_reviews_for_1_user):
    response = authorized_admin_client.delete(f'/reviews/admin/1')
    assert response.status_code == 200
    assert response.json()['message'] == 'Reviews deleted successfully'
    response = authorized_admin_client.get(f'/reviews/1')
    assert response.status_code == 404

@pytest.mark.parametrize('id, status_code', [
    (10, 404),
    (1, 403)
])
def test_delete_review_failed(authorized_client, create_reviews_for_1_product, id, status_code):
    response = authorized_client.delete(f'/reviews/{id}')
    assert response.status_code == status_code
    if status_code == 404:
        assert response.json()['detail'] == 'Review not found'
    else:
        assert response.json()['detail'] == 'You can only delete your own reviews'

def test_update_review(authorized_client, create_product):
    response = authorized_client.post('/reviews/', json={'rating': '1', 'comment': 'test', 'product_id': 1})
    assert response.status_code == 201
    response = authorized_client.put('/reviews/', json={'rating': '5', 'comment': 'test2', 'product_id': 1})
    assert response.status_code == 200
    assert response.json()['rating'] == '5'
    assert response.json()['comment'] == 'test2'
    assert response.json()['product_id'] == 1
    assert response.json()['user_id'] == 1

    #full