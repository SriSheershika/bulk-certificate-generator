
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class CertificateJob(Base):
    __tablename__ = "certificate_jobs"

    id = Column(Integer, primary_key=True, index=True)
    total_recipients = Column(Integer, nullable=False)
    successful = Column(Integer, default=0, nullable=False)
    failed = Column(Integer, default=0, nullable=False)
    status = Column(String, default="PENDING", nullable=False)

    certificates = relationship(
        "Certificate",
        back_populates="job",
        cascade="all, delete-orphan"
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(
        Integer,
        ForeignKey("certificate_jobs.id"),
        nullable=False
    )
    recipient_name = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)
    course_name = Column(String, nullable=False)
    status = Column(String, default="PENDING", nullable=False)
    file_path = Column(String, nullable=True)
    error_message = Column(String, nullable=True)

    job = relationship("CertificateJob", back_populates="certificates")
