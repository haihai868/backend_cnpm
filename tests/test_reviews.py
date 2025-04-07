import pytest

from tests.test_database_connect import db, client

def test_create_review(authorized_client, create_product):
    response = authorized_client.post('/reviews/', json={'rating': '1', 'comment': 'test', 'product_id': create_product['id']})
    assert response.status_code == 201
    assert response.json()['rating'] == '1'
    assert response.json()['comment'] == 'test'
    assert response.json()['product_id'] == create_product['id']

def test_get_review(authorized_client, create_product):
    response = authorized_client.post('/reviews/', json={'rating': '1', 'comment': 'test', 'product_id': create_product['id']})
    assert response.status_code == 201
    response = authorized_client.get(f'/reviews/{response.json()["id"]}')
    res = response.json()
    assert response.status_code == 200
    assert res['rating'] == '1'
    assert res['comment'] == 'test'
    assert res['product_id'] == create_product['id']

def test_delete_review(authorized_client, create_product):
    response = authorized_client.post('/reviews/', json={'rating': '1', 'comment': 'test', 'product_id': 1})
    assert response.status_code == 201
    del_res = authorized_client.delete(f'/reviews/{response.json()["id"]}')
    assert del_res.status_code == 200
    assert del_res.json()['message'] == 'Review deleted successfully'

    response = authorized_client.get(f'/reviews/{response.json()["id"]}')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Review not found'
