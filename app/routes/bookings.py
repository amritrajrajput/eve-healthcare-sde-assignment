from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Booking, DiagnosticCentre, DiagnosticTest, User
from app.schemas import BookingCreate, BookingResponse

router = APIRouter(prefix="/bookings", tags=["bookings"])


def owned_booking(booking_id: int, user: User, db: Session) -> Booking:
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not own this booking")
    return booking


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    centre = db.get(DiagnosticCentre, data.centre_id)
    test = db.get(DiagnosticTest, data.test_id)
    if centre is None:
        raise HTTPException(status_code=404, detail="Diagnostic centre not found")
    if test is None or test.centre_id != centre.id:
        raise HTTPException(status_code=404, detail="Diagnostic test not found at this centre")
    if data.appointment_datetime <= datetime.now(data.appointment_datetime.tzinfo):
        raise HTTPException(status_code=400, detail="Appointment must be in the future")
    booking = Booking(
        user_id=user.id,
        test_id=test.id,
        centre_id=centre.id,
        appointment_datetime=data.appointment_datetime,
        amount=test.price,
        status="PENDING",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/", response_model=list[BookingResponse])
def list_bookings(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return list(
        db.query(Booking)
        .filter(Booking.user_id == user.id)
        .order_by(Booking.id)
    )


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return owned_booking(booking_id, user, db)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    booking = owned_booking(booking_id, user, db)
    if booking.status in {"CONFIRMED", "FAILED"}:
        raise HTTPException(status_code=409, detail="Booking cannot be cancelled now")
    booking.status = "CANCELLED"
    db.commit()
    db.refresh(booking)
    return booking
