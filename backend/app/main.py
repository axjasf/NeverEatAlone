from datetime import datetime
from typing import Optional, Any, Annotated, List
from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
from typing import Iterator
from http import HTTPStatus
import sqlalchemy as sa
import logging

from backend.app.models.contact import Contact, Hashtag, EntityType, contact_hashtags

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


class ContactList(BaseModel):
    """Response model for paginated contact list."""
    items: List[ContactResponse]
    total_count: int
    limit: int = 10
    offset: int = 0


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
            last_contact=contact.last_contact,
            contact_briefing_text=contact.contact_briefing_text,
        )

        db.add(db_contact)
        if contact.hashtags:
            db_contact.set_hashtags(contact.hashtags)
        db.commit()
        db.refresh(db_contact)

        # Convert SQLAlchemy model back to Pydantic model
        db_id = getattr(db_contact.id, "_value", db_contact.id)
        return ContactResponse(
            id=UUID(str(db_id)) if not isinstance(db_id, UUID) else db_id,
            name=str(db_contact.name),
            first_name=(str(db_contact.first_name) if db_contact.first_name else None),
            sub_information=dict(db_contact.sub_information),
            hashtags=db_contact.hashtag_names,
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
        hashtags=contact.hashtag_names,
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
        if contact.hashtags is not None:  # Only update hashtags if they were provided
            db_contact.set_hashtags(contact.hashtags)
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
            hashtags=db_contact.hashtag_names,
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


@app.delete("/api/contacts/{contact_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_contact(
    contact_id: UUID, db: Annotated[Session, Depends(get_test_db)]
) -> None:
    """Delete a contact by its ID.

    Args:
        contact_id (UUID): The unique identifier of the contact to delete.
        db (Session): The database session.

    Returns:
        None: Returns no content on successful deletion.

    Raises:
        HTTPException: 404 if contact is not found.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail={"error": "Contact not found"})

    db.delete(contact)
    db.commit()


@app.get("/api/contacts", response_model=ContactList)
async def list_contacts(
    db: Annotated[Session, Depends(get_test_db)],
    name: Optional[str] = None,
    hashtags: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
) -> ContactList:
    """List contacts with pagination and filtering.

    Args:
        db (Session): The database session.
        name (str, optional): Filter by name (case-insensitive, partial match).
        hashtags (str, optional): Comma-separated list of hashtags to filter by.
        limit (int, optional): Maximum number of items to return. Defaults to 10.
        offset (int, optional): Number of items to skip. Defaults to 0.

    Returns:
        ContactList: Paginated and filtered list of contacts.
    """
    # Start with base query
    query = db.query(Contact)

    # Apply name filter if provided
    if name:
        query = query.filter(Contact._name.ilike(f"%{name}%"))

    # Apply hashtag filter if provided
    if hashtags:
        print("\n=== HASHTAG FILTERING DEBUG ===")
        print(f"Input hashtags: {hashtags}")
        tag_list = [tag.strip().lower() for tag in hashtags.split(",") if tag.strip().startswith("#")]
        print(f"Normalized tags: {tag_list}")

        # Find contacts that have ALL requested hashtags.
        matching_ids = (
            sa.select(contact_hashtags.c.contact_id)
            .join(Hashtag, contact_hashtags.c.hashtag_id == Hashtag.id)  # Explicit join condition.
            .filter(
                Hashtag.entity_type == EntityType.CONTACT,
                Hashtag.name.in_(tag_list)
            )
            .group_by(contact_hashtags.c.contact_id)
            .having(sa.func.count(sa.distinct(Hashtag.name)) == len(tag_list))
            .scalar_subquery()
        )

        # Apply filter to main query.
        query = query.filter(Contact.id.in_(matching_ids))

        print("\nDebug - Final filtered query:")
        print(str(query.statement.compile(compile_kwargs={"literal_binds": True})))

        # Print filtered results for debugging
        results = query.all()
        print(f"\nFound {len(results)} matching contacts:")
        for c in results:
            print(f"- {c.name}: {c.hashtag_names}")

    # Get total count before pagination
    total_count = query.count()
    print(f"\nTotal count: {total_count}")

    # Apply pagination
    contacts = query.offset(offset).limit(limit).all()

    # Convert to response models
    items = []
    for contact in contacts:
        db_id = getattr(contact.id, "_value", contact.id)
        items.append(
            ContactResponse(
                id=UUID(str(db_id)) if not isinstance(db_id, UUID) else db_id,
                name=str(contact.name),
                first_name=(str(contact.first_name) if contact.first_name else None),
                sub_information=dict(contact.sub_information),
                hashtags=contact.hashtag_names,
                last_contact=contact.last_contact,
                contact_briefing_text=contact.contact_briefing_text,
                created_at=contact.created_at.replace(tzinfo=None),
                updated_at=contact.updated_at.replace(tzinfo=None),
            )
        )

    return ContactList(
        items=items,
        total_count=total_count,
        limit=limit,
        offset=offset
    )
