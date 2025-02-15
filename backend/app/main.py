from datetime import datetime
from typing import Optional, Any, Annotated, List, Dict, cast
from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, field_validator, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, select, distinct, Column
from contextlib import contextmanager
from typing import Iterator
from http import HTTPStatus
import sqlalchemy as sa

from .models.domain.contact import Contact
from .models.domain.tag import EntityType
from .models.orm.contact_tag import contact_tags
from .models.orm.contact import ContactORM
from .models.orm.tag import TagORM

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


class ContactBase(BaseModel):
    """Base schema for contact data."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    first_name: Optional[str] = None
    sub_information: Dict[str, Any] = {}
    hashtags: Optional[List[str]] = None
    last_contact: Optional[datetime] = None
    contact_briefing_text: Optional[str] = None


class ContactCreate(BaseModel):
    """Schema for creating a new contact."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    first_name: Optional[str] = None
    sub_information: Dict[str, Any] = {}
    hashtags: Optional[List[str]] = None
    last_contact: Optional[datetime] = None
    contact_briefing_text: Optional[str] = None

    @field_validator("hashtags")
    @classmethod
    def validate_hashtags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate that all hashtags start with #"""
        if v is not None:
            for tag in v:
                if not tag.startswith("#"):
                    raise ValueError(f"Invalid hashtag '{tag}'. Must start with '#'")
        return v


class ContactResponse(BaseModel):
    """Schema for contact response including system fields."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID
    name: str
    first_name: Optional[str] = None
    sub_information: Dict[str, Any] = {}
    hashtags: List[str] = []  # Response always includes hashtags, even if empty
    last_contact: Optional[datetime] = None
    contact_briefing_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ContactList(BaseModel):
    """Response model for paginated contact list."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: List[ContactResponse]
    total_count: int
    limit: int
    offset: int


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
    db_contact = (
        db.query(Contact).filter(Contact.id == contact_id).first()  # type: ignore
    )
    if db_contact is None:
        raise HTTPException(status_code=404, detail={"error": "Contact not found"})

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


@app.put("/api/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    contact: ContactCreate,
    db: Annotated[Session, Depends(get_test_db)],
) -> ContactResponse:
    """Update a contact.

    Args:
        contact_id: The contact's ID
        contact: The updated contact data
        db: The database session

    Returns:
        The updated contact

    Raises:
        HTTPException: If the contact is not found or there's a database error
    """
    db_contact = (
        db.query(Contact).filter(Contact.id == contact_id).first()  # type: ignore
    )
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    try:
        # Update fields
        db_contact.name = contact.name
        db_contact.first_name = contact.first_name
        db_contact.sub_information = contact.sub_information
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
    """Delete a contact.

    Args:
        contact_id: The contact's ID
        db: The database session

    Raises:
        HTTPException: If the contact is not found
    """
    db_contact = (
        db.query(Contact).filter(Contact.id == contact_id).first()  # type: ignore
    )
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(db_contact)
    db.commit()


@app.get("/api/contacts", response_model=ContactList)
async def list_contacts(
    db: Annotated[Session, Depends(get_test_db)],
    name: Optional[str] = None,
    hashtags: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
) -> ContactList:
    """List contacts with pagination and filtering."""
    # Start with base query
    query = db.query(Contact)

    # Apply name filter if provided
    if name:
        name_col = cast(Column[str], ContactORM.name)
        query = query.filter(name_col.ilike(f"%{name}%"))

    # Apply hashtag filter if provided
    if hashtags:
        print("\n=== HASHTAG FILTERING DEBUG ===")
        print(f"Input hashtags: {hashtags}")
        tag_list = [
            tag.strip().lower()
            for tag in hashtags.split(",")
            if tag.strip().startswith("#")
        ]
        print(f"Normalized tags: {tag_list}")

        # Find contacts that have ALL requested hashtags
        matching_ids = (
            select(contact_tags.c.contact_id)
            .join(
                TagORM,
                contact_tags.c.hashtag_id == TagORM.id,
            )
            .filter(
                sa.and_(
                    TagORM.entity_type == EntityType.CONTACT.value,
                    TagORM.name.in_(tag_list)
                )
            )
            .group_by(contact_tags.c.contact_id)
            .having(func.count(distinct(TagORM.name)) == len(tag_list))
            .scalar_subquery()
        )

        # Apply filter to main query
        id_col = cast(Column[UUID], ContactORM.id)
        query = query.filter(id_col.in_(matching_ids))

        print("\nDebug - Final filtered query:")
        print(str(query.statement.compile(compile_kwargs={"literal_binds": True})))

        # Print filtered results for debugging
        results = query.all()
        print(f"\nFound {len(results)} matching contacts:")
        for c in results:
            print(f"- {c.name}: {c.hashtag_names}")

    # Get total count before pagination
    total_count = query.count()

    # Apply pagination
    contacts = query.offset(offset).limit(limit).all()

    # Convert to response models
    items: List[ContactResponse] = []
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

    return ContactList(items=items, total_count=total_count, limit=limit, offset=offset)


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Hello World"}
