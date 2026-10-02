# EVE Healthcare Backend

Small FastAPI service for diagnostic test bookings and simulated payments.

Uses only Python, FastAPI, Pydantic, SQLAlchemy, SQLite, and JWT authentication.
Postman can be used for manual API testing.

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
| POST | `/auth/signup` | No | Register and receive a JWT |
| POST | `/auth/login` | No | Login and receive a JWT |
| POST/GET | `/centres/` | POST yes | Create/list diagnostic centres |
| POST/GET | `/tests/` | POST yes | Create/list diagnostic tests |
| POST/GET | `/bookings/` | Yes | Create/list the current user's bookings |
| GET | `/bookings/{id}` | Yes | Retrieve an owned booking |
| POST | `/bookings/{id}/cancel` | Yes | Cancel a pending booking |
| POST | `/payments/` | Yes | Simulate a successful or failed payment |
| POST | `/payments/webhook/` | No | Apply an idempotent payment event |

Use `Authorization: Bearer <token>` for protected endpoints.

Example requests:

```json
POST /auth/signup
{"email":"user@example.com","password":"password123"}
```

```json
POST /bookings/
{"test_id":1,"centre_id":1,"appointment_datetime":"2030-01-01T10:00:00Z"}
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

SQLite is used by default and can be changed with `DATABASE_URL`. Users own bookings.
Bookings reference a centre and test and have one payment. Payment `event_id` is
unique, so repeated webhook events do not create duplicate payments.
