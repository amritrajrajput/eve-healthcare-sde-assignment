from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DiagnosticCentre, DiagnosticTest
from app.schemas import CentreCreate, CentreResponse, TestCreate, TestResponse

router = APIRouter(tags=["centres and tests"])


@router.post("/centres/", response_model=CentreResponse, status_code=status.HTTP_201_CREATED)
def create_centre(
    data: CentreCreate,
    db: Session = Depends(get_db),
):
    centre = DiagnosticCentre(**data.model_dump())
    db.add(centre)
    db.commit()
    db.refresh(centre)
    return centre


@router.get("/centres/", response_model=list[CentreResponse])
def list_centres(db: Session = Depends(get_db)):
    return list(db.scalars(select(DiagnosticCentre).order_by(DiagnosticCentre.id)))


@router.post("/tests/", response_model=TestResponse, status_code=status.HTTP_201_CREATED)
def create_test(
    data: TestCreate,
    db: Session = Depends(get_db),
):
    if db.get(DiagnosticCentre, data.centre_id) is None:
        raise HTTPException(status_code=404, detail="Diagnostic centre not found")
    test = DiagnosticTest(**data.model_dump())
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


@router.get("/tests/", response_model=list[TestResponse])
def list_tests(db: Session = Depends(get_db)):
    return list(db.scalars(select(DiagnosticTest).order_by(DiagnosticTest.id)))
