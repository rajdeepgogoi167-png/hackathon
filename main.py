from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from app.database import Base, engine
from app.routers import consultations, doctors, network, patients, records, signaling

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Low-Bandwidth Telemedicine API",
    description="Backend for rural consultations with adaptive quality, compression, and store-and-forward sync.",
    version="1.0.0",
)
app.add_middleware(GZipMiddleware, minimum_size=500)

app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(consultations.router)
app.include_router(network.router)
app.include_router(records.router)
app.include_router(signaling.router)


@app.get("/")
def read_root():
    return {
        "message": "Low-bandwidth telemedicine backend",
        "docs": "/docs",
        "features": [
            "adaptive video/audio/chat modes",
            "compressed medical uploads",
            "store-and-forward messaging",
            "WebRTC signaling with HTTP fallback",
        ],
    }
