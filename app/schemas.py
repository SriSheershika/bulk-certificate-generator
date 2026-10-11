
from datetime import date
from pydantic import BaseModel, Field, field_validator


class RecipientInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=254)


class BulkCertificateRequest(BaseModel):
    course_name: str = Field(min_length=1, max_length=200)
    completion_date: date
    recipients: list[RecipientInput] = Field(min_length=1, max_length=500)

    @field_validator("course_name")
    @classmethod
    def validate_course_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Course name cannot be blank")
        return value

    @field_validator("recipients")
    @classmethod
    def validate_recipients(cls, recipients):
        for recipient in recipients:
            recipient.name = recipient.name.strip()
            recipient.email = recipient.email.strip()

            if not recipient.name:
                raise ValueError("Recipient name cannot be blank")

            email = recipient.email
            if email.count("@") != 1 or "." not in email.split("@")[-1]:
                raise ValueError(f"Invalid email address: {email}")

        return recipients
