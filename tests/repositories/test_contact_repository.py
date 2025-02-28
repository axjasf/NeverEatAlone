"""Tests for the Contact repository.

Tests are organized by complexity and frequency of use:
1. Basic Tests - CRUD operations
2. Query Tests - Search and filtering
3. State Management Tests - Updates and tracking
4. Temporal Tests - Timezone handling
"""

from datetime import datetime, UTC, timedelta
from sqlalchemy.orm import Session
from backend.app.models.domain.contact_model import Contact
from backend.app.repositories.sqlalchemy_contact_repository import (
    SQLAlchemyContactRepository,
)
from backend.app.repositories.interfaces import ContactRepository
from zoneinfo import ZoneInfo


def test_contact_repository_implements_interface(db_session: Session) -> None:
    """Test that SQLAlchemyContactRepository implements ContactRepository interface.

    This test verifies architectural compliance with CR-2025.02-50.
    """
    repo = SQLAlchemyContactRepository(db_session)
    assert isinstance(repo, ContactRepository), "SQLAlchemyContactRepository must implement ContactRepository interface"


# region Basic Tests (Common)

def test_contact_save_and_find(db_session: Session) -> None:
    """Test basic CRUD operations."""
    repo = SQLAlchemyContactRepository(db_session)

    # Create and save a contact
    contact = Contact(
        name="John Doe",
        first_name="John",
        briefing_text="Important contact"
    )
    repo.save(contact)

    # Find by ID
    found = repo.find_by_id(contact.id)
    assert found is not None
    assert found.name == "John Doe"
    assert found.first_name == "John"
    assert found.briefing_text == "Important contact"


def test_contact_update(db_session: Session) -> None:
    """Test entity updates."""
    repo = SQLAlchemyContactRepository(db_session)

    # Create initial contact
    contact = Contact(name="John Doe")
    repo.save(contact)

    # Update contact
    contact.first_name = "Johnny"
    contact.briefing_text = "Updated briefing"
    contact.sub_information = {"status": "updated"}
    repo.save(contact)

    # Verify updates
    found = repo.find_by_id(contact.id)
    assert found is not None
    assert found.first_name == "Johnny"
    assert found.briefing_text == "Updated briefing"
    assert found.sub_information == {"status": "updated"}


def test_contact_delete(db_session: Session) -> None:
    """Test entity deletion."""
    repo = SQLAlchemyContactRepository(db_session)

    # Create contact
    contact = Contact(name="John Doe")
    contact.add_tag("#test")
    contact.add_note("Test note")
    repo.save(contact)

    # Verify contact exists
    found = repo.find_by_id(contact.id)
    assert found is not None

    # Delete contact
    repo.delete(contact)

    # Verify contact is gone
    found = repo.find_by_id(contact.id)
    assert found is None


def test_contact_find_all(db_session: Session) -> None:
    """Test basic query operations."""
    repo = SQLAlchemyContactRepository(db_session)

    # Create multiple contacts
    contacts = [
        Contact(name="John Doe"),
        Contact(name="Jane Doe"),
        Contact(name="Bob Smith"),
    ]
    for contact in contacts:
        repo.save(contact)

    # Find all contacts
    all_contacts = repo.find_all()
    assert len(all_contacts) == 3
    assert {c.name for c in all_contacts} == {"John Doe", "Jane Doe", "Bob Smith"}


# endregion


# region Query Tests (Common)

def test_contact_find_by_tag(db_session: Session) -> None:
    """Test tag-based queries.

    Rules:
    1. Single tag queries
    2. Multiple matches
    3. No match cases
    4. Result order
    """
    repo = SQLAlchemyContactRepository(db_session)

    # Create contacts with tags
    contact1 = Contact(name="John Doe")
    contact1.add_tag("#test")
    contact1.add_tag("#project")
    repo.save(contact1)

    contact2 = Contact(name="Jane Doe")
    contact2.add_tag("#test")
    repo.save(contact2)

    contact3 = Contact(name="Bob Smith")
    contact3.add_tag("#other")
    repo.save(contact3)

    # Find by tag
    test_contacts = repo.find_by_tag("#test")
    assert len(test_contacts) == 2
    assert {c.name for c in test_contacts} == {"John Doe", "Jane Doe"}

    project_contacts = repo.find_by_tag("#project")
    assert len(project_contacts) == 1
    assert project_contacts[0].name == "John Doe"

    other_contacts = repo.find_by_tag("#other")
    assert len(other_contacts) == 1
    assert other_contacts[0].name == "Bob Smith"


def test_contact_find_stale(db_session: Session) -> None:
    """Test frequency-based queries.

    Rules:
    1. Frequency checks
    2. Stale detection
    3. Tag handling
    4. Time thresholds
    """
    repo = SQLAlchemyContactRepository(db_session)

    # Create contacts with frequency tags
    contact1 = Contact(name="John Doe")
    contact1.add_tag("#weekly")
    tag1 = next(t for t in contact1.tags if t.name == "#weekly")
    tag1.set_frequency(7)  # Weekly
    tag1.update_last_contact(datetime.now(UTC) - timedelta(days=8))  # Stale
    repo.save(contact1)

    contact2 = Contact(name="Jane Doe")
    contact2.add_tag("#monthly")
    tag2 = next(t for t in contact2.tags if t.name == "#monthly")
    tag2.set_frequency(30)  # Monthly
    tag2.update_last_contact()  # Not stale
    repo.save(contact2)

    # Find stale contacts
    stale_contacts = repo.find_stale()
    assert len(stale_contacts) == 1
    assert stale_contacts[0].name == "John Doe"


# endregion


# region Temporal Tests (Complex)

def test_contact_timezone_handling(db_session: Session) -> None:
    """Test timezone handling.

    Rules:
    1. Timezone info
    2. UTC conversion
    3. Cross-timezone ops
    4. State consistency
    """
    repo = SQLAlchemyContactRepository(db_session)

    # Create contact with Tokyo timezone
    tokyo_time = datetime.now(ZoneInfo("Asia/Tokyo"))
    contact = Contact(name="Test Contact")
    contact.add_interaction(interaction_date=tokyo_time)
    repo.save(contact)

    # Verify timezone handling on retrieval
    found = repo.find_by_id(contact.id)
    assert found is not None
    assert found.last_contact is not None
    assert found.last_contact.tzinfo == UTC
    assert found.last_contact == tokyo_time.astimezone(UTC)

    # Update with New York timezone
    ny_time = datetime.now(ZoneInfo("America/New_York"))
    found.add_interaction(interaction_date=ny_time)
    repo.save(found)

    # Verify timezone consistency
    updated = repo.find_by_id(contact.id)
    assert updated is not None
    assert updated.last_contact is not None
    assert updated.last_contact.tzinfo == UTC
    assert updated.last_contact == ny_time.astimezone(UTC)


def test_contact_timezone_search(db_session: Session) -> None:
    """Test timezone-aware queries.

    Rules:
    1. Timezone criteria
    2. UTC conversion
    3. Cross-tz matching
    4. Time thresholds
    """
    repo = SQLAlchemyContactRepository(db_session)

    # Create contacts with different timezones
    base_time = datetime.now(UTC)

    # Contact 1: Tokyo timezone
    contact1 = Contact(name="Tokyo Contact")
    tokyo_time = base_time.astimezone(ZoneInfo("Asia/Tokyo"))
    contact1.add_interaction(interaction_date=tokyo_time)
    repo.save(contact1)

    # Contact 2: New York timezone
    contact2 = Contact(name="NY Contact")
    ny_time = base_time.astimezone(ZoneInfo("America/New_York"))
    contact2.add_interaction(interaction_date=ny_time)
    repo.save(contact2)

    # Search using different timezone criteria but same moment
    london_time = base_time.astimezone(ZoneInfo("Europe/London"))

    # All contacts should be found as they're at the same moment
    found = repo.find_by_last_contact_before(london_time + timedelta(hours=1))
    assert len(found) == 2
    assert {c.name for c in found} == {"Tokyo Contact", "NY Contact"}

    # No contacts should be found before the interaction time
    found = repo.find_by_last_contact_before(london_time - timedelta(hours=1))
    assert len(found) == 0


# endregion
