from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Doctor
from app.schemas import DoctorCreate, DoctorOut

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("", response_model=DoctorOut)
def add_doctor(payload: DoctorCreate, db: Session = Depends(get_db)):
    doctor = Doctor(name=payload.name, specialty=payload.specialty)
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.get("", response_model=list[DoctorOut])
def list_doctors(db: Session = Depends(get_db)):
    return db.query(Doctor).all()


@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor
