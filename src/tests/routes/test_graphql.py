from fastapi import status
from unittest.mock import MagicMock

def test_graphql_user(client, mock_mongo_client):
    mock_db = mock_mongo_client.get_database("users")
    mock_db.list_collection_names.return_value = ["admins"]
    
    unique_email = "graphql-unique@example.com"
    mock_user = {"username": "admin", "role": "admins", "email": unique_email}
    mock_db["admins"].find_one.return_value = mock_user
    
    query = """
    query {
        user(username: "admin") {
            username
            email
        }
    }
    """
    
    response = client.post("/graphql", json={"query": query})
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["data"]["user"]["username"] == "admin"
    assert data["data"]["user"]["email"] == unique_email