from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Booking, Payment
from app.schemas import PaymentRequest, PaymentResponse, WebhookRequest

router = APIRouter(prefix="/payments", tags=["payments"])


def apply_payment(
    booking: Booking,
    status: str,
    db: Session,
    event_id: str | None = None,
):
    if status not in {"SUCCESS", "FAILED"}:
        raise HTTPException(
            status_code=400,
            detail="Payment status must be SUCCESS or FAILED",
        )
    payment = Payment(
        booking_id=booking.id,
        amount=booking.amount,
        status=status,
        event_id=event_id,
    )
    db.add(payment)
    booking.status = "CONFIRMED" if status == "SUCCESS" else "FAILED"
    return payment


@router.post("/", response_model=PaymentResponse)
def pay(
    data: PaymentRequest,
    db: Session = Depends(get_db),
):
    booking = db.get(Booking, data.booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.payment is not None:
        raise HTTPException(status_code=409, detail="Booking has already been paid")
    payment = apply_payment(booking, "SUCCESS" if data.success else "FAILED", db)
    db.commit()
    db.refresh(payment)
    return PaymentResponse(
        payment_id=payment.id,
        booking_id=booking.id,
        status=payment.status,
    )


@router.post("/webhook/", response_model=PaymentResponse)
def webhook(data: WebhookRequest, db: Session = Depends(get_db)):
    existing = db.scalar(select(Payment).where(Payment.event_id == data.event_id))
    if existing is not None:
        return PaymentResponse(
            payment_id=existing.id,
            booking_id=existing.booking_id,
            status=existing.status,
        )
    booking = db.get(Booking, data.booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.payment is not None:
        raise HTTPException(status_code=409, detail="Booking already has a payment")
    payment = apply_payment(booking, data.status, db, data.event_id)
    db.commit()
    db.refresh(payment)
    return PaymentResponse(
        payment_id=payment.id,
        booking_id=booking.id,
        status=payment.status,
    )
