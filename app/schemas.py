from datetime import datetime

from pydantic import BaseModel, Field


class DoctorCreate(BaseModel):
    name: str
    specialty: str = "General"


class DoctorOut(BaseModel):
    id: int
    name: str
    specialty: str
    available: int

    class Config:
        from_attributes = True


class PatientCreate(BaseModel):
    name: str
    age: int = 0
    village: str = ""


class PatientOut(BaseModel):
    id: int
    name: str
    age: int
    village: str

    class Config:
        from_attributes = True


class ConsultationCreate(BaseModel):
    doctor_id: int
    patient_id: int
    symptoms: str
    bandwidth_kbps: float = Field(ge=0, default=64)
    latency_ms: float = Field(ge=0, default=400)
    packet_loss: float = Field(ge=0, le=1, default=0.05)


class ConsultationOut(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    symptoms: str
    status: str
    mode: str
    quality_profile: str
    notes: str
    created_at: datetime

    class Config:
        from_attributes = True


class NetworkProbe(BaseModel):
    consultation_id: int
    bandwidth_kbps: float
    latency_ms: float
    packet_loss: float = 0.0


class QualityDecision(BaseModel):
    mode: str
    quality_profile: str
    max_video_bitrate_kbps: int
    resolution: str
    fps: int
    audio_bitrate_kbps: int
    use_store_and_forward: bool
    reason: str


class MessageCreate(BaseModel):
    sender_role: str
    sender_id: int
    body: str


class MessageOut(BaseModel):
    id: int
    consultation_id: int
    sender_role: str
    sender_id: int
    body: str
    delivered: int
    created_at: datetime

    class Config:
        from_attributes = True


class NotesUpdate(BaseModel):
    notes: str
    status: str = "completed"


class SignalPayload(BaseModel):
    consultation_id: int
    event_type: str
    payload: str
