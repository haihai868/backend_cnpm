from http.client import responses

import pytest

from tests.test_database_connect import client, db

def test_create_notification(client, create_user):
    response = client.post('/notifications/', json={'user_id': create_user["id"], 'title': 'test', 'message': 'test'})
    assert response.status_code == 201
    assert response.json()['title'] == 'test'
    assert response.json()['message'] == 'test'
    assert response.json()['user_id'] == 1

def test_create_notification_for_all_users(client, create_user, create_user2):
    response = client.post('/notifications/users', json={'title': 'test', 'message': 'test'})
    assert response.status_code == 201

    response = client.get(f'/notifications/user/{create_user["id"]}')
    assert response.json()[0]['title'] == 'test'
    assert response.json()[0]['message'] == 'test'
    assert response.json()[0]['user_id'] == 1

    response = client.get(f'/notifications/user/{create_user2["id"]}')
    assert response.json()[0]['title'] == 'test'
    assert response.json()[0]['message'] == 'test'
    assert response.json()[0]['user_id'] == 2

def test_get_user_notifications(client, create_notifications):
    response = client.get(f'/notifications/user/{create_notifications[0]["user_id"]}')
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['title'] == create_notifications[0]['title']
    assert response.json()[0]['message'] == create_notifications[0]['message']
    assert response.json()[0]['user_id'] == create_notifications[0]['user_id']

    assert response.json()[1]['title'] == create_notifications[1]['title']
    assert response.json()[1]['message'] == create_notifications[1]['message']
    assert response.json()[1]['user_id'] == create_notifications[1]['user_id']

def test_delete_notification(authorized_client, create_notifications):
    response = authorized_client.delete(f'/notifications/{create_notifications[0]["id"]}')
    assert response.status_code == 200
    assert response.json()['message'] == 'Notification deleted successfully'
    response = authorized_client.get(f'/notifications/{create_notifications[0]["id"]}')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Notification not found'

@pytest.mark.parametrize('id, status_code', [
    (10, 404),
    (3, 403)
])
def test_delete_notification_failed(authorized_client, create_notifications, id, status_code):
    response = authorized_client.delete(f'/notifications/{id}')
    assert response.status_code == status_code
    if status_code == 404:
        assert response.json()['detail'] == 'Notification not found'
    else:
        assert response.json()['detail'] == 'You can only delete your own notifications'

def test_delete_user_notifications(authorized_client, create_notifications):
    response = authorized_client.delete(f'/notifications/')
    assert response.status_code == 200
    assert response.json()['message'] == 'Notifications deleted successfully'
    response = authorized_client.get(f'/notifications/{create_notifications[1]["id"]}')
    response1 = authorized_client.get(f'/notifications/{create_notifications[0]["id"]}')

    assert response.status_code == 404
    assert response.json()['detail'] == 'Notification not found'
    assert response1.status_code == 404
    assert response1.json()['detail'] == 'Notification not found'

def test_mark_as(authorized_client, create_notifications):
    response = authorized_client.put(f'/notifications/{create_notifications[0]["id"]}')
    assert response.status_code == 200
    assert response.json()['is_read'] == True
    response = authorized_client.put(f'/notifications/{create_notifications[0]["id"]}')
    assert response.status_code == 200
    assert response.json()['is_read'] == False

    #full