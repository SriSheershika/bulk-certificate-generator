
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app, get_db
from app.database import Base
from app import generator, main


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Create a separate test database.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Save test PDFs in a temporary folder.
    monkeypatch.setattr(
        generator,
        "OUTPUT_DIR",
        tmp_path / "certificates",
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def sample_request():
    return {
        "course_name": "Python Development",
        "completion_date": "2026-10-11",
        "recipients": [
            {
                "name": "Ananya Sharma",
                "email": "ananya@example.com",
            },
            {
                "name": "Rahul Verma",
                "email": "rahul@example.com",
            },
        ],
    }


def test_create_bulk_job(client):
    response = client.post(
        "/api/jobs/",
        json=sample_request(),
    )

    assert response.status_code == 201

    data = response.json()
    assert data["total_recipients"] == 2
    assert data["successful"] == 2
    assert data["failed"] == 0
    assert data["status"] == "COMPLETED"


def test_get_job_status(client):
    created = client.post(
        "/api/jobs/",
        json=sample_request(),
    ).json()

    response = client.get(
        f"/api/jobs/{created['job_id']}"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"
    assert len(response.json()["certificates"]) == 2


def test_invalid_input(client):
    payload = sample_request()
    payload["recipients"] = []

    response = client.post(
        "/api/jobs/",
        json=payload,
    )

    assert response.status_code == 422


def test_download_certificate(client):
    created = client.post(
        "/api/jobs/",
        json=sample_request(),
    ).json()

    job_id = created["job_id"]
    certificate_id = created["certificates"][0]["certificate_id"]

    response = client.get(
        f"/api/jobs/{job_id}/certificates/{certificate_id}/download"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_one_generation_failure_does_not_stop_others(
    client,
    monkeypatch,
):
    original_generator = main.generate_certificate

    def fail_for_first(
        certificate_id,
        recipient_name,
        course_name,
        completion_date,
    ):
        if recipient_name == "Ananya Sharma":
            raise RuntimeError("Simulated generation failure")

        return original_generator(
            certificate_id,
            recipient_name,
            course_name,
            completion_date,
        )

    monkeypatch.setattr(
        main,
        "generate_certificate",
        fail_for_first,
    )

    response = client.post(
        "/api/jobs/",
        json=sample_request(),
    )

    assert response.status_code == 201

    data = response.json()
    assert data["successful"] == 1
    assert data["failed"] == 1
    assert data["status"] == "PARTIAL_FAILURE"
