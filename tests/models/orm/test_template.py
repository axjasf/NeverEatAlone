"""Test cases for the template ORM model."""

from datetime import datetime, UTC
from uuid import uuid4
import pytest
from sqlalchemy.exc import IntegrityError, StatementError
from backend.app.models.orm.template_orm import TemplateVersionORM
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session


def test_template_version_creation(db_session: Session) -> None:
    """Test creating a template version."""
    now = datetime.now(UTC)
    template = TemplateVersionORM(
        id=uuid4(),
        version=1,
        categories={
            "contact_info": {
                "name": "contact_info",
                "description": "Basic contact information",
                "fields": {
                    "phone": {
                        "name": "phone",
                        "type": "phone",
                        "description": "Phone number",
                    }
                },
            }
        },
        created_at=now,
        updated_at=now,
    )

    db_session.add(template)
    db_session.flush()
    db_session.refresh(template)

    # Verify it was saved
    saved = db_session.get(TemplateVersionORM, (template.id, template.version))
    assert saved is not None
    assert saved.version == 1
    assert saved.categories["contact_info"]["fields"]["phone"]["type"] == "phone"
    assert saved.created_at == template.created_at
    assert saved.updated_at == template.updated_at


def test_template_version_unique_constraint(db_session: Session) -> None:
    """Test that version numbers must be unique per template."""
    template_id = uuid4()
    now = datetime.now(UTC)

    # Create first version
    v1 = TemplateVersionORM(
        id=template_id, version=1, categories={}, created_at=now, updated_at=now
    )
    db_session.add(v1)
    db_session.flush()

    # Try to create another version with the same version number
    with pytest.raises(IntegrityError):
        v2 = TemplateVersionORM(
            id=template_id, version=1, categories={}, created_at=now, updated_at=now
        )
        db_session.add(v2)
        db_session.flush()


def test_template_version_required_fields(db_session: Session) -> None:
    """Test that required fields are enforced."""
    now = datetime.now(UTC)

    # Try to create without version
    with pytest.raises(IntegrityError):
        template = TemplateVersionORM(
            id=uuid4(), categories={}, created_at=now, updated_at=now
        )
        db_session.add(template)
        db_session.flush()
    db_session.rollback()

    # Try to create without categories
    with pytest.raises(IntegrityError):
        template = TemplateVersionORM(
            id=uuid4(), version=1, created_at=now, updated_at=now
        )
        db_session.add(template)
        db_session.flush()
    db_session.rollback()


def test_template_version_json_storage(db_session: Session) -> None:
    """Test that JSON data is properly stored and retrieved."""
    now = datetime.now(UTC)
    complex_categories = {
        "personal": {
            "name": "personal",
            "description": "Personal information",
            "fields": {
                "name": {"type": "string", "required": True},
                "birth_date": {"type": "date", "format": "YYYY-MM-DD"},
                "phones": [
                    {"type": "phone", "label": "home"},
                    {"type": "phone", "label": "work"},
                ],
            },
        },
        "preferences": {
            "name": "preferences",
            "description": "Contact preferences",
            "fields": {
                "preferred_time": {
                    "type": "string",
                    "choices": ["morning", "afternoon", "evening"],
                },
                "do_not_contact": {"type": "boolean", "default": False},
            },
        },
    }

    template = TemplateVersionORM(
        id=uuid4(),
        version=1,
        categories=complex_categories,
        created_at=now,
        updated_at=now,
    )

    db_session.add(template)
    db_session.flush()

    # Verify it was saved correctly
    saved = db_session.get(TemplateVersionORM, (template.id, template.version))
    assert saved is not None
    assert saved.categories == complex_categories
    assert saved.created_at == template.created_at
    assert saved.updated_at == template.updated_at


def test_template_version_timezone_handling(db_session: Session) -> None:
    """Test that timezone information is properly stored and retrieved.

    The ORM should:
    1. Accept timezone-aware datetimes
    2. Store them in UTC
    3. Return them with UTC timezone
    4. Handle different input timezones correctly
    """
    # Create template with different timezone
    tokyo_time = datetime.now(ZoneInfo("Asia/Tokyo"))
    ny_time = datetime.now(ZoneInfo("America/New_York"))

    template = TemplateVersionORM(
        id=uuid4(),
        version=1,
        categories={},
        created_at=tokyo_time,
        updated_at=ny_time,
    )

    db_session.add(template)
    db_session.flush()
    db_session.refresh(template)

    # Verify timezone handling
    saved = db_session.get(TemplateVersionORM, (template.id, template.version))
    assert saved is not None

    # Times should be converted to UTC but represent the same moment
    assert saved.created_at.tzinfo == UTC
    assert saved.updated_at.tzinfo == UTC
    assert saved.created_at == tokyo_time.astimezone(UTC)
    assert saved.updated_at == ny_time.astimezone(UTC)


def test_template_version_naive_datetime_rejection(db_session: Session) -> None:
    """Test that naive datetimes are rejected.

    The ORM should:
    1. Reject naive datetimes (without timezone info)
    2. Raise an error with a clear message
    """
    # Try to create with naive datetime
    naive_time = datetime.now()  # Naive datetime without timezone

    with pytest.raises(StatementError, match="Cannot store naive datetime"):
        template = TemplateVersionORM(
            id=uuid4(),
            version=1,
            categories={},
            created_at=naive_time,
            updated_at=naive_time,
        )
        db_session.add(template)
        db_session.flush()
