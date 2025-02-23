"""Test cases for the template ORM model.

Tests are organized by complexity and frequency of use:
1. Basic Tests - Creation and constraints
2. Data Structure Tests - JSON storage and validation
3. Temporal Tests - Timezone handling
"""

from datetime import datetime, UTC
from uuid import uuid4
import pytest
from sqlalchemy.exc import IntegrityError, StatementError
from backend.app.models.orm.template_orm import TemplateVersionORM
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session


# region Basic Tests (Common)

def test_template_version_creation(db_session: Session) -> None:
    """Test basic template version creation."""
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
    """Test version number uniqueness."""
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
    """Test required field validation."""
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


# endregion


# region Data Structure Tests (Complex)

def test_template_version_json_storage(db_session: Session) -> None:
    """Test complex JSON data storage.

    Verifies:
    1. Nested object storage
    2. Array handling
    3. Mixed data types
    4. Deep object graphs
    """
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


# endregion


# region Temporal Tests (Complex)

def test_template_version_timezone_handling(db_session: Session) -> None:
    """Test timezone handling.

    Verifies:
    1. Timezone-aware datetime acceptance
    2. UTC storage
    3. Timezone preservation
    4. Cross-timezone operations
    """
    # Create template with different timezone
    tokyo_time = datetime.now(ZoneInfo("Asia/Tokyo"))
    ny_time = tokyo_time.astimezone(ZoneInfo("America/New_York"))  # Same moment

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

    # Test DST transition
    ny_tz = ZoneInfo("America/New_York")
    winter_time = datetime(2024, 1, 1, 12, 0, tzinfo=ny_tz)  # During EST
    summer_time = datetime(2024, 7, 1, 12, 0, tzinfo=ny_tz)  # During EDT

    winter_template = TemplateVersionORM(
        id=uuid4(),
        version=1,
        categories={},
        created_at=winter_time,
        updated_at=winter_time
    )
    db_session.add(winter_template)
    db_session.flush()
    db_session.refresh(winter_template)

    summer_template = TemplateVersionORM(
        id=uuid4(),
        version=1,
        categories={},
        created_at=summer_time,
        updated_at=summer_time
    )
    db_session.add(summer_template)
    db_session.flush()
    db_session.refresh(summer_template)

    # Verify DST handling
    assert winter_template.created_at == winter_time.astimezone(UTC)
    assert summer_template.created_at == summer_time.astimezone(UTC)

    # Test fractional offset (India UTC+5:30)
    india_tz = ZoneInfo("Asia/Kolkata")
    india_time = datetime(2024, 1, 1, 1, 0, tzinfo=india_tz)
    india_template = TemplateVersionORM(
        id=uuid4(),
        version=1,
        categories={},
        created_at=india_time,
        updated_at=india_time
    )
    db_session.add(india_template)
    db_session.flush()
    db_session.refresh(india_template)

    assert india_template.created_at == india_time.astimezone(UTC)

    # Test day boundary transition
    tokyo_tz = ZoneInfo("Asia/Tokyo")
    ny_midnight = datetime(2024, 1, 1, 0, 0, tzinfo=ny_tz)
    tokyo_time = ny_midnight.astimezone(tokyo_tz)

    ny_template = TemplateVersionORM(
        id=uuid4(),
        version=1,
        categories={},
        created_at=ny_midnight,
        updated_at=ny_midnight
    )
    db_session.add(ny_template)
    db_session.flush()
    db_session.refresh(ny_template)

    tokyo_template = TemplateVersionORM(
        id=uuid4(),
        version=1,
        categories={},
        created_at=tokyo_time,
        updated_at=tokyo_time
    )
    db_session.add(tokyo_template)
    db_session.flush()
    db_session.refresh(tokyo_template)

    # Verify both represent the same moment in UTC
    assert ny_template.created_at == tokyo_template.created_at


def test_template_version_naive_datetime_rejection(db_session: Session) -> None:
    """Test naive datetime rejection.

    Verifies:
    1. Rejection of naive datetimes
    2. Clear error messaging
    3. Validation consistency
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


# endregion
