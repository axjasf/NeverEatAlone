"""Tests for the Contact ORM model.

Tests are organized by complexity and frequency of use:
1. Basic Tests - Creation and constraints
2. Data Structure Tests - JSON storage
3. Relationship Tests - Notes and tags
4. Temporal Tests - Timezone handling
"""

import pytest
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Session
from backend.app.models.orm.contact_orm import ContactORM
from backend.app.models.orm.note_orm import NoteORM
from backend.app.models.orm.tag_orm import TagORM
from backend.app.models.domain.tag_model import EntityType
from datetime import datetime, UTC
from uuid import uuid4
from zoneinfo import ZoneInfo


# region Basic Tests (Common)

def test_contact_creation_with_required_fields(db_session: Session) -> None:
    """Test basic creation with required fields."""
    contact = ContactORM(name="John Doe")
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)

    saved_contact = db_session.get(ContactORM, contact.id)
    assert saved_contact is not None
    assert saved_contact.name == "John Doe"
    assert saved_contact.first_name is None
    assert saved_contact.briefing_text is None
    assert saved_contact.sub_information == {}


def test_contact_creation_with_all_fields(db_session: Session) -> None:
    """Test creation with all optional fields."""
    sub_info = {"family_status": "Married", "professional_situation": "CEO"}

    contact = ContactORM(
        name="John Doe",
        first_name="John",
        briefing_text="Important business contact",
        sub_information=sub_info,
    )
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)

    saved_contact = db_session.get(ContactORM, contact.id)
    assert saved_contact is not None
    assert saved_contact.name == "John Doe"
    assert saved_contact.first_name == "John"
    assert saved_contact.briefing_text == "Important business contact"
    assert saved_contact.sub_information == sub_info


def test_contact_name_required(db_session: Session) -> None:
    """Test required field constraints."""
    contact = ContactORM()  # type: ignore
    db_session.add(contact)
    with pytest.raises(IntegrityError):
        db_session.commit()


# endregion


# region Data Structure Tests (Complex)

def test_contact_sub_information_json_storage(db_session: Session) -> None:
    """Test complex JSON data persistence.

    Verifies:
    1. Nested object storage
    2. Array handling
    3. Mixed data types
    4. Deep object graphs
    """
    sub_info = {
        "personal": {
            "hobbies": ["reading", "hiking"],
            "family": {"status": "married", "children": 2},
        },
        "professional": {"role": "developer", "skills": ["python", "typescript"]},
    }
    contact = ContactORM(name="John Doe", sub_information=sub_info)
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)

    saved_contact = db_session.get(ContactORM, contact.id)
    assert saved_contact is not None
    assert saved_contact.sub_information == sub_info


# endregion


# region Relationship Tests (Common)

def test_contact_note_relationship(db_session: Session) -> None:
    """Test note relationships.

    Verifies:
    1. Note addition
    2. Order preservation
    3. Cascade deletion
    4. Relationship integrity
    """
    contact = ContactORM(name="John Doe")
    db_session.add(contact)

    # Add notes
    note1 = NoteORM(contact=contact, content="First note")
    note2 = NoteORM(contact=contact, content="Second note")
    db_session.add(note1)
    db_session.add(note2)
    db_session.commit()

    # Verify notes were added
    saved_contact = db_session.get(ContactORM, contact.id)
    assert saved_contact is not None
    assert len(saved_contact.notes) == 2
    assert saved_contact.notes[0].content == "First note"
    assert saved_contact.notes[1].content == "Second note"

    # Test cascade delete
    db_session.delete(saved_contact)
    db_session.commit()
    assert db_session.query(NoteORM).count() == 0


def test_contact_tag_relationship(db_session: Session) -> None:
    """Test tag relationships.

    Verifies:
    1. Tag addition
    2. No cascade deletion
    3. Many-to-many integrity
    4. Order preservation
    """
    contact = ContactORM(name="John Doe")
    db_session.add(contact)
    db_session.commit()  # Save contact first to get its ID

    # Add tags
    tag1 = TagORM(
        name="#test", entity_id=contact.id, entity_type=EntityType.CONTACT.value
    )
    tag2 = TagORM(
        name="#project", entity_id=contact.id, entity_type=EntityType.CONTACT.value
    )

    # Add tags to session and save them to get IDs
    db_session.add(tag1)
    db_session.add(tag2)
    db_session.commit()

    # Now associate tags with contact
    contact.tags.extend([tag1, tag2])
    db_session.commit()

    # Verify tags were added
    saved_contact = db_session.get(ContactORM, contact.id)
    assert saved_contact is not None
    assert len(saved_contact.tags) == 2
    assert sorted(t.name for t in saved_contact.tags) == ["#project", "#test"]

    # Test that tags are not cascade deleted
    db_session.delete(saved_contact)
    db_session.commit()
    assert db_session.query(TagORM).count() == 2


# endregion


# region Temporal Tests (Complex)

def test_contact_timezone_handling(db_session: Session) -> None:
    """Test timezone handling.

    Verifies:
    1. Timezone-aware input
    2. UTC storage
    3. Timezone preservation
    4. Cross-timezone operations
    """
    # Create contact with different timezone
    tokyo_time = datetime.now(ZoneInfo("Asia/Tokyo"))
    ny_time = datetime.now(ZoneInfo("America/New_York"))

    contact = ContactORM(
        id=uuid4(),
        name="Test Contact",
        last_contact=tokyo_time,
    )

    db_session.add(contact)
    db_session.flush()
    db_session.refresh(contact)

    # Verify timezone handling
    saved = db_session.get(ContactORM, contact.id)
    assert saved is not None

    # Times should be converted to UTC but represent the same moment
    assert saved.last_contact is not None
    assert saved.last_contact.tzinfo == UTC
    assert saved.last_contact == tokyo_time.astimezone(UTC)

    # Update with different timezone
    saved.last_contact = ny_time
    db_session.flush()
    db_session.refresh(saved)

    assert saved.last_contact == ny_time.astimezone(UTC)
    assert saved.last_contact.tzinfo == UTC


def test_contact_naive_datetime_rejection(db_session: Session) -> None:
    """Test naive datetime rejection.

    Verifies:
    1. Rejection of naive datetimes
    2. Clear error messaging
    3. Validation consistency
    """
    # Try to create with naive datetime
    naive_time = datetime.now()  # Naive datetime without timezone

    with pytest.raises(StatementError, match="Cannot store naive datetime"):
        contact = ContactORM(
            id=uuid4(),
            name="Test Contact",
            last_contact=naive_time,
        )
        db_session.add(contact)
        db_session.flush()


# endregion
