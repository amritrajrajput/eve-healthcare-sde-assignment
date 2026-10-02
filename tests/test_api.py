from datetime import datetime, timedelta, timezone

from tests.conftest import auth_headers


def setup_catalog(client, token):
    headers = auth_headers(token)
    centre = client.post(
        "/centres/", json={"name": "Central Lab", "location": "Downtown"}, headers=headers
    ).json()
    test = client.post(
        "/tests/",
        json={"name": "Blood Test", "price": "25.00", "centre_id": centre["id"]},
        headers=headers,
    ).json()
    return headers, centre, test


def create_booking(client, token):
    headers, centre, test = setup_catalog(client, token)
    appointment = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    booking = client.post(
        "/bookings/",
        json={
            "test_id": test["id"],
            "centre_id": centre["id"],
            "appointment_datetime": appointment,
        },
        headers=headers,
    )
    return headers, booking


def test_signup_login_and_protected_route(client):
    signup = client.post(
        "/auth/signup", json={"email": "a@example.com", "password": "password123"}
    )
    assert signup.status_code == 201
    login = client.post(
        "/auth/login", json={"email": "a@example.com", "password": "password123"}
    )
    assert login.status_code == 200
    assert client.get("/bookings/").status_code == 401


def test_booking_and_payment_success(client, user_token):
    headers, booking_response = create_booking(client, user_token)
    assert booking_response.status_code == 201
    booking = booking_response.json()
    payment = client.post(
        "/payments/", json={"booking_id": booking["id"], "success": True}, headers=headers
    )
    assert payment.status_code == 200
    assert payment.json()["status"] == "SUCCESS"
    assert client.get(f"/bookings/{booking['id']}", headers=headers).json()["status"] == "CONFIRMED"


def test_failed_payment_and_duplicate_webhook(client, user_token):
    headers, booking_response = create_booking(client, user_token)
    booking = booking_response.json()
    failed = client.post(
        "/payments/", json={"booking_id": booking["id"], "success": False}, headers=headers
    )
    assert failed.status_code == 200
    assert failed.json()["status"] == "FAILED"

    headers2, booking_response2 = create_booking(client, user_token)
    booking2 = booking_response2.json()
    event = {"event_id": "evt-1", "booking_id": booking2["id"], "status": "SUCCESS"}
    first = client.post("/payments/webhook/", json=event)
    second = client.post("/payments/webhook/", json=event)
    assert first.status_code == second.status_code == 200
    assert first.json()["payment_id"] == second.json()["payment_id"]


def test_invalid_resources_and_ownership(client, user_token):
    headers = auth_headers(user_token)
    future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    invalid_centre = client.post(
        "/bookings/",
        json={"test_id": 1, "centre_id": 999, "appointment_datetime": future},
        headers=headers,
    )
    assert invalid_centre.status_code == 404
    invalid_test = client.post(
        "/bookings/",
        json={"test_id": 999, "centre_id": 1, "appointment_datetime": future},
        headers=headers,
    )
    assert invalid_test.status_code == 404
    headers, booking_response = create_booking(client, user_token)
    assert booking_response.status_code == 201
    assert client.get("/bookings/999", headers=headers).status_code == 404
    other = client.post(
        "/auth/signup", json={"email": "other@example.com", "password": "password123"}
    ).json()["access_token"]
    booking_id = booking_response.json()["id"]
    assert client.get(f"/bookings/{booking_id}", headers=auth_headers(other)).status_code == 403
