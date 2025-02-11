from datetime import datetime, UTC
from typing import Optional, Any
from uuid import UUID, uuid4
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Contact Management API")


class ContactCreate(BaseModel):
    """Schema for creating a new contact"""

    name: str
    first_name: Optional[str] = None
    sub_information: Optional[dict[str, Any]] = None
    hashtags: Optional[list[str]] = None
    last_contact: Optional[datetime] = None


class ContactResponse(ContactCreate):
    """Schema for contact response including system fields"""

    id: UUID
    created_at: datetime
    updated_at: datetime


@app.post("/api/contacts", response_model=ContactResponse, status_code=201)
async def create_contact(contact: ContactCreate) -> ContactResponse:
    """Create a new contact with the provided data"""
    now = datetime.now(UTC)
    return ContactResponse(
        **contact.model_dump(),
        id=uuid4(),
        created_at=now,
        updated_at=now
    )
