import pytest
from tests.test_database_connect import client, db

def test_create_category(client):
    response = client.post('/categories/', json={'name': 'test_category', 'description': 'test_desc'})
    assert response.status_code == 201

def test_create_category_failed(client, create_category):
    response = client.post('/categories/', json={'name': 'test_category', 'description': 'test_desc'})
    assert response.status_code == 400
    assert response.json()['detail'] == 'Category already exists'

def test_get_by_name(client, create_category):
    response = client.get(f'/categories/{create_category["name"]}')
    assert response.status_code == 200
    assert response.json()['name'] == create_category['name']
    assert response.json()['description'] == create_category['description']

def test_get_by_name_failed(client):
    response = client.get(f'/categories/test_category')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Category not found'

    #full