from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CentreCreate(BaseModel):
    name: str = Field(min_length=1)
    location: str = Field(min_length=1)


class CentreResponse(CentreCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TestCreate(BaseModel):
    name: str = Field(min_length=1)
    price: Decimal = Field(gt=0)
    centre_id: int = Field(gt=0)


class TestResponse(TestCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class BookingCreate(BaseModel):
    patient_email: str = Field(
        min_length=3,
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    test_id: int = Field(gt=0)
    centre_id: int = Field(gt=0)
    appointment_datetime: datetime


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    patient_email: str
    test_id: int
    centre_id: int
    appointment_datetime: datetime
    amount: Decimal
    status: str


class PaymentRequest(BaseModel):
    booking_id: int = Field(gt=0)
    success: bool = True


class PaymentResponse(BaseModel):
    payment_id: int
    booking_id: int
    status: str


class WebhookRequest(BaseModel):
    event_id: str = Field(min_length=1)
    booking_id: int = Field(gt=0)
    status: str
