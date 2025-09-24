import pytest

def test_create_department(client):
    response = client.post(
        "/departments/create",
        json={"name": "KMF"}
    )
    assert response.status_code == 200
    # assert response.json() == {"name": "kmf"}
