"""Contact Management API."""

# Standard library imports
from contextlib import contextmanager
from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Any, Dict, Iterator, List, Optional, TypeVar, Union, cast
from uuid import UUID

# Third-party imports
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import sqlalchemy as sa

# Local imports
from .models.domain.contact_model import Contact
from .models.domain.tag_model import EntityType
from .models.orm.contact_tag_orm import contact_tags as contact_hashtags
from .models.orm.contact_orm import ContactORM
from .models.orm.tag_orm import TagORM

# Type variables
T = TypeVar("T")

# Type definitions
ErrorDetail = Union[str, Dict[str, Any], None]

# FastAPI application
app = FastAPI(
    title="Contact Management API",
    description="API for managing contacts and their relationships",
)

# Test database session store
_test_db: Optional[Session] = None


def get_test_db() -> Session:
    """Get database session for testing.

    Returns:
        Session: The test database session.

    Raises:
        RuntimeError: If no test database session is found.
    """
    if _test_db is None:
        raise RuntimeError(
            "No database session found. "
            "Make sure you're running this through the test client."
        )
    return _test_db


@contextmanager
def override_get_db(db: Session) -> Iterator[None]:
    """Context manager to override the database session during tests.

    Args:
        db: The database session to use.
    """
    global _test_db
    _test_db = db
    try:
        yield
    finally:
        _test_db = None


class ContactBase(BaseModel):
    """Base schema for contact data."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "first_name": "John",
                "briefing_text": "Important business contact",
                "sub_information": {"role": "developer"},
                "hashtags": ["#work", "#tech"],
            }
        },
    )

    name: str
    first_name: Optional[str] = None
    briefing_text: Optional[str] = None
    sub_information: Dict[str, Any] = Field(default_factory=dict)
    hashtags: List[str] = Field(
        default_factory=list,
        description="List of hashtags. Each tag must start with '#'.",
    )

    @field_validator("hashtags")
    @classmethod
    def validate_hashtags(cls, v: List[str]) -> List[str]:
        """Validate that all hashtags start with #."""
        return [tag if tag.startswith("#") else f"#{tag}" for tag in v]


class ContactCreate(BaseModel):
    """Schema for creating a new contact."""

    name: str
    first_name: Optional[str] = None
    briefing_text: Optional[str] = None
    sub_information: Dict[str, Any] = Field(default_factory=dict)
    hashtags: Optional[List[str]] = Field(
        default=None,
        description="List of hashtags. Each tag must start with '#'.",
    )

    @field_validator("hashtags")
    @classmethod
    def validate_hashtags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate that all hashtags start with #."""
        if v is not None:
            return [tag if tag.startswith("#") else f"#{tag}" for tag in v]
        return v


class ContactResponse(BaseModel):
    """Schema for contact response including system fields."""

    id: UUID
    name: str
    first_name: Optional[str] = None
    briefing_text: Optional[str] = None
    sub_information: Dict[str, Any] = Field(default_factory=dict)
    hashtags: List[str] = Field(
        default_factory=list,
        description="List of hashtags. Each tag must start with '#'.",
    )
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
    """Handle request validation errors.

    Args:
        request: The incoming request.
        exc: The validation exception.

    Returns:
        A JSON response with the error details.
    """
    error_msg: str = exc.errors()[0]["msg"] if exc.errors() else "Validation error"
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content={"error": error_msg},
    )


def _format_error_detail(detail: ErrorDetail) -> Dict[str, str]:
    """Format error detail into a consistent structure.

    Args:
        detail: The error detail from an exception.

    Returns:
        A dictionary with an error message.
    """
    # Default error message
    DEFAULT_ERROR = "Unknown error"

    try:
        # Handle None case
        if detail is None:
            return {"error": DEFAULT_ERROR}

        # Handle dictionary case with error key
        if (
            isinstance(detail, dict)
            and "error" in detail
            and isinstance(detail["error"], str)
        ):
            return {"error": detail["error"]}

        # Handle string case (all other cases converted to string)
        return {"error": str(detail)}
    except Exception:
        return {"error": DEFAULT_ERROR}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions.

    Args:
        request: The incoming request.
        exc: The HTTP exception.

    Returns:
        A JSON response with the error details.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=_format_error_detail(exc.detail),
    )


@app.post(
    "/api/contacts", response_model=ContactResponse, status_code=HTTPStatus.CREATED
)
async def create_contact(
    contact: ContactCreate,
    db: Annotated[Session, Depends(get_test_db)],
) -> ContactResponse:
    """Create a new contact.

    Args:
        contact: The contact data to create.
        db: The database session.

    Returns:
        The created contact.

    Raises:
        HTTPException: If the contact data is invalid.
    """
    try:
        # Convert Pydantic model to domain model
        db_contact = Contact(
            name=contact.name,
            first_name=contact.first_name,
            briefing_text=contact.briefing_text,
            sub_information=contact.sub_information or {},
        )

        # Add contact and its tags
        db.add(db_contact)
        if contact.hashtags:
            for tag_name in contact.hashtags:
                db_contact.add_tag(tag_name)

        db.commit()
        db.refresh(db_contact)

        # Convert to response model
        return _contact_to_response(db_contact)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"error": "Invalid data provided"},
        )


def _contact_to_response(contact: Contact | ContactORM) -> ContactResponse:
    """Convert a domain or ORM contact model to a response model."""
    db_id = getattr(contact.id, "_value", contact.id)
    return ContactResponse(
        id=UUID(str(db_id)) if not isinstance(db_id, UUID) else db_id,
        name=str(contact.name),
        first_name=(str(contact.first_name) if contact.first_name else None),
        briefing_text=contact.briefing_text,
        sub_information=dict(contact.sub_information),
        hashtags=[tag.name for tag in contact.tags],
        created_at=contact.created_at.replace(tzinfo=None),
        updated_at=contact.updated_at.replace(tzinfo=None),
    )


@app.get("/api/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    db: Annotated[Session, Depends(get_test_db)],
) -> ContactResponse:
    """Get a contact by ID."""
    db_contact = db.query(ContactORM).filter(ContactORM.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": "Contact not found"},
        )

    return _contact_to_response(cast(Contact, db_contact))


@app.put("/api/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    contact: ContactCreate,
    db: Annotated[Session, Depends(get_test_db)],
) -> ContactResponse:
    """Update a contact."""
    db_contact = db.query(ContactORM).filter(ContactORM.id == contact_id).first()
    if not db_contact:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": "Contact not found"},
        )

    try:
        # Convert to domain model for update
        domain_contact = Contact(
            name=contact.name,
            first_name=contact.first_name,
            briefing_text=contact.briefing_text,
            sub_information=contact.sub_information or {},
        )

        # Update ORM fields from domain model
        db_contact.name = str(domain_contact.name)
        if domain_contact.first_name is not None:
            db_contact.first_name = str(domain_contact.first_name)
        if domain_contact.briefing_text is not None:
            db_contact.briefing_text = str(domain_contact.briefing_text)
        db_contact.sub_information = dict(domain_contact.sub_information)

        # Update tags if provided
        if contact.hashtags is not None:
            # Clear existing tags
            db_contact.tags = []
            # Add new tags
            for tag_name in contact.hashtags:
                tag_name = tag_name if tag_name.startswith("#") else f"#{tag_name}"
                tag = TagORM(
                    entity_id=db_contact.id,
                    entity_type=EntityType.CONTACT.value,
                    name=tag_name.lower(),
                )
                db_contact.tags.append(tag)

        db.commit()
        db.refresh(db_contact)

        return _contact_to_response(cast(Contact, db_contact))

    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"error": str(e)},
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"error": "Invalid data provided"},
        )


@app.delete("/api/contacts/{contact_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_contact(
    contact_id: UUID,
    db: Annotated[Session, Depends(get_test_db)],
) -> None:
    """Delete a contact."""
    db_contact = db.query(ContactORM).filter(ContactORM.id == contact_id).first()
    if not db_contact:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": "Contact not found"},
        )

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
    query = db.query(ContactORM)

    # Apply name filter if provided
    if name:
        # cspell:ignore ilike
        query = query.filter(ContactORM.name.ilike(f"%{name}%"))

    # Apply hashtag filter if provided
    if hashtags:
        tag_list = [
            tag.strip().lower()
            for tag in hashtags.split(",")
            if tag.strip().startswith("#")
        ]

        # Find contacts that have ALL requested hashtags
        matching_ids = (
            select(contact_hashtags.c.contact_id)
            .join(
                TagORM,
                contact_hashtags.c.hashtag_id == TagORM.id,
            )
            .filter(
                TagORM.entity_type == EntityType.CONTACT.value,
                TagORM.name.in_(tag_list),
            )
            .group_by(contact_hashtags.c.contact_id)
            .having(sa.func.count(sa.distinct(TagORM.name)) == len(tag_list))
            .scalar_subquery()
        )

        # Apply filter to main query
        query = query.filter(ContactORM.id.in_(matching_ids))

    # Get total count before pagination
    total_count = query.count()

    # Apply pagination
    contacts = query.offset(offset).limit(limit).all()

    # Convert to response models
    items = [_contact_to_response(cast(Contact, contact)) for contact in contacts]

    return ContactList(
        items=items,
        total_count=total_count,
        limit=limit,
        offset=offset,
    )


@app.get("/")
def read_root() -> Dict[str, str]:
    """Root endpoint for health checks."""
    return {"message": "Hello World"}
