# EVE Healthcare Backend

Small FastAPI service for diagnostic test bookings and simulated payments.

Uses Python, FastAPI, Pydantic, SQLAlchemy, and SQLite.
Postman can be used for manual API testing.

## Project files

- `app/main.py` starts the API.
- `app/models.py` defines the database tables.
- `app/schemas.py` validates request and response data.
- `app/routes/` contains the API endpoints.
- `healthcare.db` is the local SQLite database.

## Simple flow

1. Create a centre and a test.
2. Book the test with the patient's email.
3. Make a simulated payment.
4. Send the same webhook more than once; it is processed only once.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API: `http://127.0.0.1:8000`  
Swagger UI: `http://127.0.0.1:8000/docs`

## Required API

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| POST/GET | `/centres/` | No | Create/list diagnostic centres |
| POST/GET | `/tests/` | No | Create/list diagnostic tests |
| POST/GET | `/bookings/` | No | Create/list bookings |
| GET | `/bookings/{id}` | No | Retrieve a booking |
| POST | `/bookings/{id}/cancel` | No | Cancel a pending booking |
| POST | `/payments/` | No | Simulate a successful or failed payment |
| POST | `/payments/webhook/` | No | Apply an idempotent payment event |

Example requests:

```json
POST /bookings/
{"patient_email":"user@example.com","test_id":1,"centre_id":1,"appointment_datetime":"2030-01-01T10:00:00Z"}
```

```json
POST /payments/
{"booking_id":1,"success":true}
```

```json
POST /payments/webhook/
{"event_id":"evt-123","booking_id":1,"status":"SUCCESS"}
```

## Database

SQLite stores the data in `healthcare.db`. Users own bookings. Bookings reference a
centre and test and have one payment. Payment `event_id` is unique, so repeated
webhook events do not create duplicate payments.

## AI assistance

I am learning backend development. I used AI tools to explain FastAPI concepts,
review the code, and simplify the documentation. I checked the final code and
behavior locally.
