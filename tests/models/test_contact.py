import pytest
from datetime import datetime, UTC, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend.app.models.contact import Contact, Tag, EntityType


def test_contact_creation_with_required_fields(db_session: Session) -> None:
    """Test creating a contact with only required fields."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)

    saved_contact = db_session.get(Contact, contact.id)
    assert saved_contact is not None
    assert saved_contact.name == "John Doe"
    assert saved_contact.first_name is None
    assert saved_contact.briefing_text is None
    assert saved_contact.sub_information == {}
    assert saved_contact.tags == []


def test_contact_creation_with_all_fields(db_session: Session) -> None:
    """Test creating a contact with all available fields."""
    sub_info = {"family_status": "Married", "professional_situation": "CEO"}
    tags = ["#business", "#vip"]

    contact = Contact(name="John Doe")
    contact.first_name = "John"
    contact.briefing_text = "Important business contact"
    contact.sub_information = sub_info
    db_session.add(contact)
    contact.set_tags(tags)

    db_session.commit()
    db_session.refresh(contact)

    saved_contact = db_session.get(Contact, contact.id)
    assert saved_contact is not None
    assert saved_contact.name == "John Doe"
    assert saved_contact.first_name == "John"
    assert saved_contact.briefing_text == "Important business contact"
    assert saved_contact.sub_information == sub_info
    assert [t.name for t in saved_contact.tags] == tags


def test_contact_name_required(db_session: Session) -> None:
    """Test that contact creation fails when name is not provided."""
    contact = Contact()
    db_session.add(contact)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_contact_sub_information_validation(db_session: Session) -> None:
    """Test that sub_information must be a valid dictionary."""
    with pytest.raises(ValueError):
        Contact(name="John Doe", sub_information="invalid")


def test_contact_sub_information_empty_dict(db_session: Session) -> None:
    """Test that sub_information can be an empty dictionary."""
    contact = Contact(name="John Doe", sub_information={})
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)

    saved_contact = db_session.get(Contact, contact.id)
    assert saved_contact is not None
    assert saved_contact.sub_information == {}


def test_contact_sub_information_nested_dict(db_session: Session) -> None:
    """Test that sub_information supports nested dictionaries."""
    sub_info = {
        "personal": {
            "hobbies": ["reading", "hiking"],
            "family": {"status": "married", "children": 2},
        },
        "professional": {
            "role": "developer",
            "skills": ["python", "typescript"]
        },
    }
    contact = Contact(name="John Doe", sub_information=sub_info)
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)

    saved_contact = db_session.get(Contact, contact.id)
    assert saved_contact is not None
    assert saved_contact.sub_information == sub_info


def test_contact_sub_information_update(db_session: Session) -> None:
    """Test updating sub_information fields."""
    contact = Contact(name="John Doe", sub_information={"role": "developer"})
    db_session.add(contact)
    db_session.commit()

    contact.sub_information = {"role": "manager", "team": "engineering"}
    db_session.commit()
    db_session.refresh(contact)

    saved_contact = db_session.get(Contact, contact.id)
    assert saved_contact is not None
    assert saved_contact.sub_information == {
        "role": "manager",
        "team": "engineering"
    }


def test_contact_tags_validation(db_session: Session) -> None:
    """Test that tags must be a valid list."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    with pytest.raises(ValueError):
        contact.set_tags("invalid")  # type: ignore


def test_contact_tag_format(db_session: Session) -> None:
    """Test that tags must start with #."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    with pytest.raises(ValueError):
        contact.set_tags(["invalid"])  # Should raise error - no # prefix


def test_tag_case_normalization(db_session: Session) -> None:
    """Test that tags are normalized to lowercase."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    contact.set_tags(["#TEST", "#CamelCase"])
    db_session.commit()
    db_session.refresh(contact)

    assert sorted(t.name for t in contact.tags) == sorted(["#test", "#camelcase"])


def test_tag_uniqueness_per_entity(db_session: Session) -> None:
    """Test that tags are unique per entity."""
    # Create two contacts with the same tag
    contact1 = Contact(name="John Doe")
    contact2 = Contact(name="Jane Doe")

    db_session.add(contact1)
    db_session.add(contact2)

    contact1.set_tags(["#test"])
    contact2.set_tags(["#test"])

    db_session.commit()
    db_session.refresh(contact1)
    db_session.refresh(contact2)

    # Each contact should have its own tag instance
    assert len(db_session.query(Tag).filter_by(
        name="#test",
        entity_type=EntityType.CONTACT
    ).all()) == 2
    assert [t.name for t in contact1.tags] == ["#test"]
    assert [t.name for t in contact2.tags] == ["#test"]


def test_tag_entity_type(db_session: Session) -> None:
    """Test that tags are created with correct entity type."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    contact.set_tags(["#test"])
    db_session.commit()
    db_session.refresh(contact)

    tag = db_session.query(Tag).filter_by(
        entity_id=contact.id,
        name="#test",
        entity_type=EntityType.CONTACT
    ).first()
    assert tag is not None
    assert tag.entity_type == EntityType.CONTACT


def test_tag_frequency_tracking(db_session: Session) -> None:
    """Test tracking frequency and staleness of contact tags."""
    # Create a contact with a weekly tag
    contact = Contact(name="John Doe")
    db_session.add(contact)
    contact.set_tags(["#weekly"])
    db_session.commit()

    # Get the weekly tag
    weekly_tag = contact.tags[0]

    # Set frequency and last contact
    weekly_tag.set_frequency(7)
    weekly_tag.update_last_contact()
    db_session.commit()

    # Tag should not be stale yet
    assert not weekly_tag.is_stale()

    # Move last_contact to 8 days ago
    weekly_tag.update_last_contact(datetime.now(UTC) - timedelta(days=8))
    db_session.commit()

    # Tag should now be stale
    assert weekly_tag.is_stale()
    assert weekly_tag.staleness_days == 1


def test_tag_frequency_validation(db_session: Session) -> None:
    """Test validation of tag frequency settings."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    contact.set_tags(["#weekly"])
    db_session.commit()

    tag = contact.tags[0]

    # Test valid frequency range
    tag.set_frequency(1)  # Minimum valid frequency
    assert tag.frequency_days == 1
    tag.set_frequency(365)  # Maximum valid frequency
    assert tag.frequency_days == 365

    # Test invalid frequencies
    with pytest.raises(ValueError, match="between 1 and 365"):
        tag.set_frequency(0)
    with pytest.raises(ValueError, match="between 1 and 365"):
        tag.set_frequency(366)
    with pytest.raises(ValueError, match="between 1 and 365"):
        tag.set_frequency(-1)


def test_tag_last_contact_tracking(db_session: Session) -> None:
    """Test tracking last contact date."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    contact.set_tags(["#weekly"])
    db_session.commit()

    tag = contact.tags[0]
    tag.set_frequency(7)

    # Update last contact with default (now)
    tag.update_last_contact()
    assert tag.last_contact is not None
    assert (datetime.now(UTC) - tag.last_contact).total_seconds() < 1

    # Update with specific date
    specific_date = datetime.now(UTC) - timedelta(days=3)
    tag.update_last_contact(specific_date)
    assert tag.last_contact == specific_date


def test_tag_staleness_calculation_basic(db_session: Session) -> None:
    """Test basic staleness calculation scenarios."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    contact.set_tags(["#weekly"])
    db_session.commit()

    tag = contact.tags[0]

    # No frequency set - should not be stale
    assert not tag.is_stale()
    assert tag.staleness_days is None

    # Set frequency but no last contact - should not be stale
    tag.set_frequency(7)
    assert not tag.is_stale()
    assert tag.staleness_days is None

    # Set last contact to now - should not be stale
    tag.update_last_contact()
    assert not tag.is_stale()
    assert tag.staleness_days == 0

    # Set last contact to 8 days ago - should be stale
    tag.update_last_contact(datetime.now(UTC) - timedelta(days=8))
    assert tag.is_stale()
    assert tag.staleness_days == 1


def test_tag_frequency_disable(db_session: Session) -> None:
    """Test disabling frequency tracking."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    contact.set_tags(["#weekly"])
    db_session.commit()

    tag = contact.tags[0]
    tag.set_frequency(7)
    tag.update_last_contact()
    assert tag.frequency_days is not None
    assert tag.last_contact is not None

    # Disable tracking
    tag.disable_frequency()
    assert tag.frequency_days is None
    assert tag.last_contact is None
    assert not tag.is_stale()
    assert tag.staleness_days is None


def test_multiple_tag_frequencies(db_session: Session) -> None:
    """Test handling multiple tags with different frequencies."""
    # Create a contact with multiple tags
    contact = Contact(name="John Doe")
    db_session.add(contact)
    contact.set_tags(["#weekly", "#monthly"])
    db_session.commit()

    # Set different frequencies
    weekly_tag = next(t for t in contact.tags if t.name == "#weekly")
    monthly_tag = next(t for t in contact.tags if t.name == "#monthly")

    weekly_tag.set_frequency(7)
    monthly_tag.set_frequency(30)

    now = datetime.now(UTC)
    weekly_tag.update_last_contact(now - timedelta(days=10))  # Overdue
    monthly_tag.update_last_contact(now - timedelta(days=20))  # Not overdue
    db_session.commit()

    assert weekly_tag.is_stale()
    assert not monthly_tag.is_stale()
    assert weekly_tag.staleness_days == 3
    assert monthly_tag.staleness_days == 0
