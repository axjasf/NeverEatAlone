"""Tests for the Contact repository."""

import pytest
from datetime import datetime, UTC, timedelta
from sqlalchemy.orm import Session
from backend.app.models.domain.contact import Contact
from backend.app.models.domain.tag import Tag, EntityType
from backend.app.models.orm.contact import ContactORM
from backend.app.models.repositories.sqlalchemy_contact_repository import (
    SQLAlchemyContactRepository,
)


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
