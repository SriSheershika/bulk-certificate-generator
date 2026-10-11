
# Bulk Certificate Generator API

A Python backend application that generates PDF certificates in bulk using FastAPI, SQLAlchemy, SQLite, and ReportLab.

## Features

- Generate certificates for multiple recipients in one API request.
- Validate incoming recipient and course information.
- Generate personalized PDF certificates using a predefined template.
- Track job status and individual certificate results.
- Continue processing other recipients if one certificate fails.
- Retrieve job information and download generated PDFs.
- Automated tests for core functionality and failure handling.

## Technology Stack

- Python 3.12
- FastAPI
- SQLite
- SQLAlchemy
- ReportLab
- Pytest

## Project Structure

```text
bulk-certificate-generator/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── generator.py
├── tests/
│   └── test_api.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

Create and activate a virtual environment.

Windows PowerShell:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run the Application

```powershell
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

### 1. Create a bulk certificate job

`POST /api/jobs/`

Example request:

```json
{
  "course_name": "Python Development",
  "completion_date": "2026-10-11",
  "recipients": [
    {
      "name": "Ananya Sharma",
      "email": "ananya@example.com"
    },
    {
      "name": "Rahul Verma",
      "email": "rahul@example.com"
    }
  ]
}
```

The response includes the job ID, overall status, success and failure counts, and individual certificate results.

### 2. Retrieve job status

`GET /api/jobs/{job_id}`

Returns the job status and the status of each certificate.

### 3. Download a certificate

`GET /api/jobs/{job_id}/certificates/{certificate_id}/download`

Returns the generated PDF when the certificate is available.

### 4. Health check

`GET /`

Returns a message confirming that the API is running.

## Architecture

The FastAPI application receives and validates requests using Pydantic schemas. SQLAlchemy stores generation jobs and certificate records in SQLite. ReportLab generates personalized PDF files from a predefined template.

Each recipient is processed independently. Successful and failed results are recorded in the database, and the job status reflects the overall result.

## Design Decisions

- FastAPI provides REST endpoints and interactive API documentation.
- SQLite provides a lightweight relational database suitable for local development.
- SQLAlchemy separates database operations from API logic.
- ReportLab generates PDFs directly in Python.
- Synchronous processing keeps the initial implementation simple.
- Per-certificate exception handling allows other recipients to be processed when one generation fails.

## Testing

Run the automated tests:

```powershell
python -m pytest -v
```

The tests cover bulk job creation, job status retrieval, input validation, certificate download, and individual generation failure handling.

## Learning Outcomes

- Building REST APIs with FastAPI.
- Validating request data with Pydantic.
- Modeling relational data using SQLAlchemy.
- Generating PDF documents programmatically.
- Handling partial failures in bulk operations.
- Writing automated API tests.

## Future Scope

- Add background workers for asynchronous processing.
- Provide real-time progress tracking.
- Add authentication and authorization.
- Support configurable certificate templates.
- Add email delivery and ZIP downloads for bulk results.
- Introduce persistent file storage and deployment monitoring.

## Limitations

Generation currently runs synchronously within the API request. The application is intended as a foundational implementation and would need additional safeguards, background processing, and production storage configuration for large-scale deployment.
