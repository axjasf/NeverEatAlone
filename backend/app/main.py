from datetime import datetime
from typing import Optional, Any, Annotated
from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator
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
    hashtags: Optional[list[str]] = Field(
        None, description="List of hashtags. Each tag must start with '#'."
    )
    last_contact: Optional[datetime] = None
    contact_briefing_text: Optional[str] = None

    @field_validator("hashtags")
    @classmethod
    def validate_hashtags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate that all hashtags start with #"""
        if v is not None:
            for tag in v:
                if not tag.startswith("#"):
                    raise ValueError("Each hashtag must be a string starting with #")
        return v

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
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Convert validation errors to our standard format"""
    error_msg: str = exc.errors()[0]["msg"] if exc.errors() else "Validation error"
    return JSONResponse(status_code=400, content={"error": error_msg})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Convert HTTP exceptions to our standard format"""
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(status_code=exc.status_code, content={"error": str(detail)})


@app.post("/api/contacts", response_model=ContactResponse, status_code=201)
async def create_contact(
    contact: ContactCreate, db: Annotated[Session, Depends(get_test_db)]
) -> ContactResponse:
    """Create a new contact with the provided data.

    Args:
        contact (ContactCreate): The contact data to create.
        db (Session): The database session.

    Returns:
        ContactResponse: The created contact with system fields.

    Raises:
        HTTPException: 400 if data is invalid or constraints are violated.
    """
    try:
        # Convert Pydantic model to SQLAlchemy model
        db_contact = Contact(
            name=contact.name,
            first_name=contact.first_name,
            sub_information=contact.sub_information or {},
            hashtags=contact.hashtags or [],
            last_contact=contact.last_contact,
            contact_briefing_text=contact.contact_briefing_text,
        )

        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)

        # Convert SQLAlchemy model back to Pydantic model
        db_id = getattr(db_contact.id, "_value", db_contact.id)
        return ContactResponse(
            id=UUID(str(db_id)) if not isinstance(db_id, UUID) else db_id,
            name=str(db_contact.name),
            first_name=(str(db_contact.first_name) if db_contact.first_name else None),
            sub_information=dict(db_contact.sub_information),
            hashtags=list(db_contact.hashtags),
            last_contact=db_contact.last_contact,
            contact_briefing_text=db_contact.contact_briefing_text,
            created_at=db_contact.created_at.replace(tzinfo=None),
            updated_at=db_contact.updated_at.replace(tzinfo=None),
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail={"error": "Invalid data provided"})


@app.get("/api/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID, db: Annotated[Session, Depends(get_test_db)]
) -> ContactResponse:
    """Retrieve a contact by its ID.

    Args:
        contact_id (UUID): The unique identifier of the contact.
        db (Session): The database session.

    Returns:
        ContactResponse: The requested contact data.

    Raises:
        HTTPException: 404 if contact is not found.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail={"error": "Contact not found"})

    db_id = getattr(contact.id, "_value", contact.id)
    return ContactResponse(
        id=UUID(str(db_id)) if not isinstance(db_id, UUID) else db_id,
        name=str(contact.name),
        first_name=(str(contact.first_name) if contact.first_name else None),
        sub_information=dict(contact.sub_information),
        hashtags=list(contact.hashtags),
        last_contact=contact.last_contact,
        contact_briefing_text=contact.contact_briefing_text,
        created_at=contact.created_at.replace(tzinfo=None),
        updated_at=contact.updated_at.replace(tzinfo=None),
    )


@app.put("/api/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    contact: ContactCreate,
    db: Annotated[Session, Depends(get_test_db)],
) -> ContactResponse:
    """Update an existing contact.

    Args:
        contact_id (UUID): The unique identifier of the contact to update.
        contact (ContactCreate): The new contact data.
        db (Session): The database session.

    Returns:
        ContactResponse: The updated contact data.

    Raises:
        HTTPException: 404 if contact is not found, 400 if data is invalid.
    """
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail={"error": "Contact not found"})

    try:
        # Prepare and validate all data before making changes
        hashtags = contact.hashtags or []
        sub_info = contact.sub_information or {}

        # Validate hashtags
        for tag in hashtags:
            if not tag.startswith("#"):
                raise ValueError("Each hashtag must be a string starting with #")

        # Validate sub_information
        if not isinstance(sub_info, dict):
            raise ValueError("Input should be a valid dictionary")

        # Update fields only after all validation passes
        db_contact.name = contact.name
        db_contact.first_name = contact.first_name
        db_contact.sub_information = sub_info
        db_contact.hashtags = hashtags
        db_contact.last_contact = contact.last_contact
        db_contact.contact_briefing_text = contact.contact_briefing_text

        db.commit()
        db.refresh(db_contact)

        # Convert to response model
        db_id = getattr(db_contact.id, "_value", db_contact.id)
        return ContactResponse(
            id=UUID(str(db_id)) if not isinstance(db_id, UUID) else db_id,
            name=str(db_contact.name),
            first_name=(str(db_contact.first_name) if db_contact.first_name else None),
            sub_information=dict(db_contact.sub_information),
            hashtags=list(db_contact.hashtags),
            last_contact=db_contact.last_contact,
            contact_briefing_text=db_contact.contact_briefing_text,
            created_at=db_contact.created_at.replace(tzinfo=None),
            updated_at=db_contact.updated_at.replace(tzinfo=None),
        )
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail={"error": str(e)})
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail={"error": "Invalid data provided"})
