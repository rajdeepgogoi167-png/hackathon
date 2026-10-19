from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.compression import jpeg_quality_for_bandwidth, save_compressed
from app.database import get_db
from app.models import Consultation, MedicalRecord, Patient

router = APIRouter(prefix="/records", tags=["records"])


@router.post("")
async def upload_record(
    patient_id: int = Form(...),
    consultation_id: int | None = Form(default=None),
    bandwidth_kbps: float = Form(default=64),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not db.get(Patient, patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    if consultation_id and not db.get(Consultation, consultation_id):
        raise HTTPException(status_code=404, detail="Consultation not found")

    raw = await file.read()
    quality = jpeg_quality_for_bandwidth(bandwidth_kbps)
    path, compressed_size = save_compressed(
        raw,
        file.filename or "record.bin",
        file.content_type or "application/octet-stream",
        quality,
    )
    record = MedicalRecord(
        patient_id=patient_id,
        consultation_id=consultation_id,
        original_name=file.filename or "record.bin",
        stored_path=str(path),
        mime_type=file.content_type or "application/octet-stream",
        original_bytes=len(raw),
        compressed_bytes=compressed_size,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    saved = max(len(raw) - compressed_size, 0)
    return {
        "id": record.id,
        "original_name": record.original_name,
        "original_bytes": record.original_bytes,
        "compressed_bytes": record.compressed_bytes,
        "bytes_saved": saved,
        "ratio": round(compressed_size / len(raw), 3) if raw else 0,
        "jpeg_quality": quality,
    }


@router.get("/patient/{patient_id}")
def list_records(patient_id: int, db: Session = Depends(get_db)):
    if not db.get(Patient, patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    records = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).all()
    return [
        {
            "id": item.id,
            "original_name": item.original_name,
            "original_bytes": item.original_bytes,
            "compressed_bytes": item.compressed_bytes,
            "consultation_id": item.consultation_id,
        }
        for item in records
    ]


@router.get("/{record_id}/download")
def download_record(record_id: int, db: Session = Depends(get_db)):
    record = db.get(MedicalRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return FileResponse(record.stored_path, filename=record.original_name)
