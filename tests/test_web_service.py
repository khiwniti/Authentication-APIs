import pytest
from fastapi.testclient import TestClient

def test_webhook_endpoint(test_client):
    response = test_client.post(
        "/api/v1/web-service/webhook",
        json={
            "event_type": "user.created",
            "data": {"user_id": "123", "email": "test@example.com"}
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_callback_endpoint(test_client):
    response = test_client.post(
        "/api/v1/web-service/callback/payment",
        json={
            "transaction_id": "tx_123",
            "status": "success"
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

@pytest.mark.asyncio
async def test_notification_endpoint(test_client, authenticated_user):
    response = test_client.post(
        "/api/v1/web-service/notify",
        json={
            "notification_type": "email",
            "recipient": "user@example.com",
            "data": {"subject": "Test", "body": "Test message"}
        },
        headers={"Authorization": f"Bearer {authenticated_user['access_token']}"}
    )
    assert response.status_code == 202 