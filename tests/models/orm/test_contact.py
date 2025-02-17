"""Tests for the Contact ORM model."""

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


def test_contact_creation_with_required_fields(db_session: Session) -> None:
    """Test creating a contact with only required fields."""
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
    """Test creating a contact with all available fields."""
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
    """Test that name is required."""
    contact = ContactORM()  # type: ignore
    db_session.add(contact)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_contact_sub_information_json_storage(db_session: Session) -> None:
    """Test that sub_information is properly stored as JSON."""
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


def test_contact_note_relationship(db_session: Session) -> None:
    """Test the relationship between contacts and notes."""
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
    """Test the relationship between contacts and tags."""
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


def test_contact_creation(db_session: Session) -> None:
    """Test creating a contact."""
    now = datetime.now(UTC)
    contact = ContactORM(
        id=uuid4(),
        name="Test Contact",
        first_name="Test",
        briefing_text="Test briefing",
        sub_information={"key": "value"},
        last_contact=now,
        contact_briefing_text="Last interaction",
    )

    db_session.add(contact)
    db_session.flush()
    db_session.refresh(contact)

    # Verify it was saved
    saved = db_session.get(ContactORM, contact.id)
    assert saved is not None
    assert saved.name == "Test Contact"
    assert saved.first_name == "Test"
    assert saved.briefing_text == "Test briefing"
    assert saved.sub_information == {"key": "value"}
    assert saved.last_contact == now
    assert saved.contact_briefing_text == "Last interaction"


def test_contact_timezone_handling(db_session: Session) -> None:
    """Test that timezone information is properly stored and retrieved.

    The ORM should:
    1. Accept timezone-aware datetimes
    2. Store them in UTC
    3. Return them with UTC timezone
    4. Handle different input timezones correctly
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
    """Test that naive datetimes are rejected.

    The ORM should:
    1. Reject naive datetimes (without timezone info)
    2. Raise an error with a clear message
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
