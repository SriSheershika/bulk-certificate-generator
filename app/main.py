
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models import CertificateJob, Certificate
from app.schemas import BulkCertificateRequest
from app.generator import generate_certificate


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Bulk Certificate Generator API",
    description="Generate and retrieve certificates in bulk.",
    version="1.0.0",
    lifespan=lifespan,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Bulk Certificate Generator API is running"}


@app.post("/api/jobs/", status_code=201)
def create_job(
    request: BulkCertificateRequest,
    db: Session = Depends(get_db)
):
    job = CertificateJob(
        total_recipients=len(request.recipients),
        successful=0,
        failed=0,
        status="PROCESSING",
    )
    db.add(job)
    db.flush()

    certificates = []
    for recipient in request.recipients:
        certificate = Certificate(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            course_name=request.course_name,
            status="PENDING",
        )
        db.add(certificate)
        certificates.append(certificate)

    db.commit()
    db.refresh(job)

    # Generate each certificate independently so one failure
    # does not stop the remaining recipients.
    for certificate in certificates:
        try:
            certificate.status = "PROCESSING"
            db.commit()

            certificate.file_path = generate_certificate(
                certificate_id=certificate.id,
                recipient_name=certificate.recipient_name,
                course_name=certificate.course_name,
                completion_date=request.completion_date.isoformat(),
            )
            certificate.status = "COMPLETED"
            certificate.error_message = None
            job.successful += 1

        except Exception as exc:
            certificate.status = "FAILED"
            certificate.error_message = str(exc)[:500]
            job.failed += 1

        db.commit()

    if job.failed == 0:
        job.status = "COMPLETED"
    elif job.successful == 0:
        job.status = "FAILED"
    else:
        job.status = "PARTIAL_FAILURE"

    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "status": job.status,
        "total_recipients": job.total_recipients,
        "successful": job.successful,
        "failed": job.failed,
        "certificates": [
            {
                "certificate_id": cert.id,
                "recipient_name": cert.recipient_name,
                "status": cert.status,
                "error": cert.error_message,
            }
            for cert in certificates
        ],
    }


@app.get("/api/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(CertificateJob, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.id,
        "status": job.status,
        "total_recipients": job.total_recipients,
        "successful": job.successful,
        "failed": job.failed,
        "certificates": [
            {
                "certificate_id": cert.id,
                "recipient_name": cert.recipient_name,
                "recipient_email": cert.recipient_email,
                "status": cert.status,
                "error": cert.error_message,
            }
            for cert in job.certificates
        ],
    }


@app.get("/api/jobs/{job_id}/certificates/{certificate_id}/download")
def download_certificate(
    job_id: int,
    certificate_id: int,
    db: Session = Depends(get_db),
):
    certificate = db.get(Certificate, certificate_id)

    if not certificate or certificate.job_id != job_id:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found for this job",
        )

    if certificate.status != "COMPLETED" or not certificate.file_path:
        raise HTTPException(
            status_code=409,
            detail="Certificate is not available for download",
        )

    path = Path(certificate.file_path)

    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Generated certificate file is missing",
        )

    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename=f"certificate_{certificate.id}.pdf",
    )
