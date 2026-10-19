from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.adaptive import decide_quality
from app.database import get_db
from app.models import Consultation, Doctor, Message, NetworkReport, Patient
from app.schemas import (
    ConsultationCreate,
    ConsultationOut,
    MessageCreate,
    MessageOut,
    NotesUpdate,
)

router = APIRouter(prefix="/consultations", tags=["consultations"])


@router.post("", response_model=ConsultationOut)
def create_consultation(payload: ConsultationCreate, db: Session = Depends(get_db)):
    if not db.get(Doctor, payload.doctor_id):
        raise HTTPException(status_code=404, detail="Doctor not found")
    if not db.get(Patient, payload.patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")

    decision = decide_quality(payload.bandwidth_kbps, payload.latency_ms, payload.packet_loss)
    consultation = Consultation(
        doctor_id=payload.doctor_id,
        patient_id=payload.patient_id,
        symptoms=payload.symptoms,
        status="queued" if decision.use_store_and_forward else "live",
        mode=decision.mode,
        quality_profile=decision.quality_profile,
    )
    db.add(consultation)
    db.flush()
    db.add(
        NetworkReport(
            consultation_id=consultation.id,
            bandwidth_kbps=payload.bandwidth_kbps,
            latency_ms=payload.latency_ms,
            packet_loss=payload.packet_loss,
            recommended_mode=decision.mode,
            recommended_profile=decision.quality_profile,
        )
    )
    db.commit()
    db.refresh(consultation)
    return consultation


@router.get("", response_model=list[ConsultationOut])
def list_consultations(db: Session = Depends(get_db)):
    return db.query(Consultation).order_by(Consultation.id.desc()).all()


@router.get("/{consultation_id}", response_model=ConsultationOut)
def get_consultation(consultation_id: int, db: Session = Depends(get_db)):
    consultation = db.get(Consultation, consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return consultation


@router.post("/{consultation_id}/notes", response_model=ConsultationOut)
def add_notes(consultation_id: int, payload: NotesUpdate, db: Session = Depends(get_db)):
    consultation = db.get(Consultation, consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    consultation.notes = payload.notes
    consultation.status = payload.status
    db.commit()
    db.refresh(consultation)
    return consultation


@router.post("/{consultation_id}/messages", response_model=MessageOut)
def queue_message(consultation_id: int, payload: MessageCreate, db: Session = Depends(get_db)):
    consultation = db.get(Consultation, consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    message = Message(
        consultation_id=consultation_id,
        sender_role=payload.sender_role,
        sender_id=payload.sender_id,
        body=payload.body,
        delivered=0,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get("/{consultation_id}/messages", response_model=list[MessageOut])
def list_messages(consultation_id: int, pending_only: bool = False, db: Session = Depends(get_db)):
    if not db.get(Consultation, consultation_id):
        raise HTTPException(status_code=404, detail="Consultation not found")
    query = db.query(Message).filter(Message.consultation_id == consultation_id)
    if pending_only:
        query = query.filter(Message.delivered == 0)
    return query.order_by(Message.id.asc()).all()


@router.post("/{consultation_id}/messages/sync", response_model=list[MessageOut])
def sync_messages(consultation_id: int, db: Session = Depends(get_db)):
    """Mark queued store-and-forward messages as delivered once the client reconnects."""
    if not db.get(Consultation, consultation_id):
        raise HTTPException(status_code=404, detail="Consultation not found")
    pending = (
        db.query(Message)
        .filter(Message.consultation_id == consultation_id, Message.delivered == 0)
        .all()
    )
    for message in pending:
        message.delivered = 1
    db.commit()
    return pending
