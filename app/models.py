from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    specialty: Mapped[str] = mapped_column(String(120), default="General")
    available: Mapped[int] = mapped_column(Integer, default=1)

    consultations = relationship("Consultation", back_populates="doctor")


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    age: Mapped[int] = mapped_column(Integer, default=0)
    village: Mapped[str] = mapped_column(String(120), default="")

    consultations = relationship("Consultation", back_populates="patient")
    records = relationship("MedicalRecord", back_populates="patient")


class Consultation(Base):
    __tablename__ = "consultations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"))
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    symptoms: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="queued")
    mode: Mapped[str] = mapped_column(String(40), default="store_and_forward")
    quality_profile: Mapped[str] = mapped_column(String(40), default="ultra_low")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    doctor = relationship("Doctor", back_populates="consultations")
    patient = relationship("Patient", back_populates="consultations")
    messages = relationship("Message", back_populates="consultation")


class NetworkReport(Base):
    __tablename__ = "network_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    consultation_id: Mapped[int] = mapped_column(ForeignKey("consultations.id"))
    bandwidth_kbps: Mapped[float] = mapped_column(Float)
    latency_ms: Mapped[float] = mapped_column(Float)
    packet_loss: Mapped[float] = mapped_column(Float, default=0.0)
    recommended_mode: Mapped[str] = mapped_column(String(40))
    recommended_profile: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    consultation_id: Mapped[int | None] = mapped_column(ForeignKey("consultations.id"), nullable=True)
    original_name: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str] = mapped_column(String(80), default="application/octet-stream")
    original_bytes: Mapped[int] = mapped_column(Integer, default=0)
    compressed_bytes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="records")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    consultation_id: Mapped[int] = mapped_column(ForeignKey("consultations.id"))
    sender_role: Mapped[str] = mapped_column(String(20))
    sender_id: Mapped[int] = mapped_column(Integer)
    body: Mapped[str] = mapped_column(Text)
    delivered: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    consultation = relationship("Consultation", back_populates="messages")


class SignalingEvent(Base):
    __tablename__ = "signaling_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    consultation_id: Mapped[int] = mapped_column(ForeignKey("consultations.id"))
    event_type: Mapped[str] = mapped_column(String(40))
    payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
