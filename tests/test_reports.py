from tests.test_database_connect import client, db

def test_create_report(authorized_client, create_user):
    response = authorized_client.post('/reports/', json={'message': 'test'})
    assert response.status_code == 201
    assert response.json()['message'] == 'test'
    assert response.json()['fullname'] == create_user['fullname']
    assert response.json()['created_at'] is not None
    assert response.json()['id'] == 1

def test_get_all_reports(authorized_client):
    response = authorized_client.post('/reports/', json={'message': 'test'})
    assert response.status_code == 201
    create_report = response.json()

    response = authorized_client.post('/reports/', json={'message': 'test2'})
    assert response.status_code == 201
    create_report2 = response.json()

    response = authorized_client.get('/reports/')
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['message'] == create_report['message']
    assert response.json()[0]['created_at'] == create_report['created_at']
    assert response.json()[0]['id'] == create_report['id']

    assert response.json()[1]['message'] == create_report2['message']
    assert response.json()[1]['created_at'] == create_report2['created_at']
    assert response.json()[1]['id'] == create_report2['id']

def test_delete_report(authorized_client, create_report):
    response = authorized_client.delete(f'/reports/{create_report["id"]}')
    assert response.status_code == 200
    assert response.json()['message'] == 'Report deleted successfully'
    response = authorized_client.get(f'/reports/{create_report["id"]}')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Report not found'

def test_delete_report_failed(authorized_client, create_report):
    response = authorized_client.delete(f'/reports/{create_report["id"] + 1}')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Report not found'

def test_update_report(authorized_client, create_report):
    response = authorized_client.put(f'/reports/{create_report["id"]}', json={'message': 'test2'})
    assert response.status_code == 200
    assert response.json()['message'] == 'test2'
    assert response.json()['fullname'] == create_report['fullname']
    assert response.json()['created_at'] == create_report['created_at']
    assert response.json()['id'] == create_report['id']

def test_get_reports_by_user_id(authorized_client, create_report):
    response = authorized_client.get(f'/reports/users/1')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['message'] == create_report['message']
    assert response.json()[0]['created_at'] == create_report['created_at']
    assert response.json()[0]['id'] == create_report['id']

def test_admin_update_report(authorized_admin_client, create_report):
    response = authorized_admin_client.put(f'/reports/admin/{create_report["id"]}', json={'message': 'test2'})
    assert response.status_code == 200
    assert response.json()['message'] == 'test2'
    assert response.json()['fullname'] == create_report['fullname']
    assert response.json()['created_at'] == create_report['created_at']