from datetime import datetime
from typing import Optional, Any, Annotated
from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
from typing import Iterator

from backend.app.models.contact import Contact

app = FastAPI(title="Contact Management API")

# Store for the test database session
_test_db: Optional[Session] = None


def get_test_db() -> Session:
    """Get database session - using test session for now"""
    if _test_db is None:
        raise RuntimeError(
            "No database session found. "
            "Make sure you're running this through the test client."
        )
    return _test_db


@contextmanager
def override_get_db(db: Session) -> Iterator[None]:
    """Context manager to override the database session during tests"""
    global _test_db
    _test_db = db
    try:
        yield
    finally:
        _test_db = None


class ContactCreate(BaseModel):
    """Schema for creating a new contact"""
    name: str = Field(..., min_length=1, max_length=100)
    first_name: Optional[str] = None
    sub_information: Optional[dict[str, Any]] = None
    hashtags: Optional[list[str]] = None
    last_contact: Optional[datetime] = None
    contact_briefing_text: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "first_name": "John",
                "sub_information": {"role": "developer"},
                "hashtags": ["#work", "#tech"],
            }
        }
    }


class ContactResponse(ContactCreate):
    """Schema for contact response including system fields"""
    id: UUID
    created_at: datetime
    updated_at: datetime


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Convert validation errors to our standard format"""
    error_msg: str = (
        exc.errors()[0]["msg"] if exc.errors() else "Validation error"
    )
    return JSONResponse(
        status_code=400,
        content={"error": error_msg}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """Convert HTTP exceptions to our standard format"""
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=detail
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(detail)}
    )


@app.post("/api/contacts", response_model=ContactResponse, status_code=201)
async def create_contact(
    contact: ContactCreate,
    db: Annotated[Session, Depends(get_test_db)]
) -> ContactResponse:
    """Create a new contact with the provided data"""
    try:
        # Convert Pydantic model to SQLAlchemy model
        db_contact = Contact(
            name=contact.name,
            first_name=contact.first_name,
            sub_information=contact.sub_information or {},
            hashtags=contact.hashtags or [],
            last_contact=contact.last_contact,
            contact_briefing_text=contact.contact_briefing_text
        )

        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)

        # Convert SQLAlchemy model back to Pydantic model
        db_id = getattr(db_contact.id, '_value', db_contact.id)
        return ContactResponse(
            id=UUID(str(db_id)) if not isinstance(db_id, UUID) else db_id,
            name=str(db_contact.name),
            first_name=(
                str(db_contact.first_name) if db_contact.first_name else None
            ),
            sub_information=dict(db_contact.sub_information),
            hashtags=list(db_contact.hashtags),
            last_contact=db_contact.last_contact,
            contact_briefing_text=db_contact.contact_briefing_text,
            created_at=db_contact.created_at.replace(tzinfo=None),
            updated_at=db_contact.updated_at.replace(tzinfo=None)
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid data provided"}
        )


@app.get("/api/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    db: Annotated[Session, Depends(get_test_db)]
) -> ContactResponse:
    """Retrieve a contact by ID"""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "Contact not found"}
        )

    db_id = getattr(contact.id, '_value', contact.id)
    return ContactResponse(
        id=UUID(str(db_id)) if not isinstance(db_id, UUID) else db_id,
        name=str(contact.name),
        first_name=(
            str(contact.first_name) if contact.first_name else None
        ),
        sub_information=dict(contact.sub_information),
        hashtags=list(contact.hashtags),
        last_contact=contact.last_contact,
        contact_briefing_text=contact.contact_briefing_text,
        created_at=contact.created_at.replace(tzinfo=None),
        updated_at=contact.updated_at.replace(tzinfo=None)
    )
