"""Tests for the Contact repository."""

from datetime import datetime, UTC, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session
from backend.app.models.domain.contact_model import Contact
from backend.app.repositories.sqlalchemy_contact_repository import (
    SQLAlchemyContactRepository,
)
from zoneinfo import ZoneInfo


def test_contact_save_and_find(db_session: Session) -> None:
    """Test saving and finding a contact."""
    repo = SQLAlchemyContactRepository(db_session)

    # Create and save a contact
    contact = Contact(
        name="John Doe", first_name="John", briefing_text="Important business contact"
    )
    repo.save(contact)

    # Find by ID
    found = repo.find_by_id(contact.id)
    assert found is not None
    assert found.name == "John Doe"
    assert found.first_name == "John"
    assert found.briefing_text == "Important business contact"


def test_contact_find_by_tag(db_session: Session) -> None:
    """Test finding contacts by tag."""
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
    """Test finding contacts with stale tags."""
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


def test_contact_update(db_session: Session) -> None:
    """Test updating a contact."""
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
    """Test deleting a contact."""
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
    """Test finding all contacts."""
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


def test_contact_timezone_handling(db_session: Session) -> None:
    """Test timezone handling in the repository layer.

    The repository should:
    1. Preserve timezone information when saving
    2. Return timezone-aware datetimes in UTC
    3. Handle different input timezones correctly
    4. Maintain timezone consistency across operations
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
    """Test timezone handling in repository search operations.

    The repository should:
    1. Handle timezone-aware dates in search operations
    2. Convert search criteria to UTC internally
    3. Return consistent results regardless of input timezone
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
