import pytest
from datetime import datetime, UTC, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend.app.models.contact import Contact, Hashtag, EntityType


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
    assert saved_contact.contact_briefing_text is None
    assert saved_contact.sub_information == {}
    assert saved_contact.hashtag_names == []


def test_contact_creation_with_all_fields(db_session: Session) -> None:
    """Test creating a contact with all available fields."""
    sub_info = {"family_status": "Married", "professional_situation": "CEO"}
    hashtags = ["#business", "#vip"]

    contact = Contact(name="John Doe")
    contact.first_name = "John"
    contact.contact_briefing_text = "Important business contact"
    contact.sub_information = sub_info
    db_session.add(contact)
    contact.set_hashtags(hashtags)

    db_session.commit()
    db_session.refresh(contact)

    saved_contact = db_session.get(Contact, contact.id)
    assert saved_contact is not None
    assert saved_contact.name == "John Doe"
    assert saved_contact.first_name == "John"
    assert saved_contact.contact_briefing_text == "Important business contact"
    assert saved_contact.sub_information == sub_info
    assert saved_contact.hashtag_names == hashtags


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


def test_contact_hashtags_validation(db_session: Session) -> None:
    """Test that hashtags must be a valid list."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    with pytest.raises(ValueError):
        contact.set_hashtags("invalid")  # type: ignore


def test_contact_hashtag_format(db_session: Session) -> None:
    """Test that hashtags must start with #."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    with pytest.raises(ValueError):
        contact.set_hashtags(["invalid"])  # Should raise error - no # prefix


def test_hashtag_case_normalization(db_session: Session) -> None:
    """Test that hashtags are normalized to lowercase."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    contact.set_hashtags(["#TEST", "#CamelCase"])
    db_session.commit()
    db_session.refresh(contact)

    assert contact.hashtag_names == ["#test", "#camelcase"]


def test_hashtag_uniqueness(db_session: Session) -> None:
    """Test that hashtags are unique per entity type."""
    # Create two contacts with the same hashtag
    contact1 = Contact(name="John Doe")
    contact2 = Contact(name="Jane Doe")

    db_session.add(contact1)
    db_session.add(contact2)

    contact1.set_hashtags(["#test"])
    contact2.set_hashtags(["#test"])

    db_session.commit()
    db_session.refresh(contact1)
    db_session.refresh(contact2)

    # Both should reference the same hashtag entity
    assert len(db_session.query(Hashtag).filter_by(
        name="#test",
        entity_type=EntityType.CONTACT
    ).all()) == 1
    assert contact1.hashtag_names == ["#test"]
    assert contact2.hashtag_names == ["#test"]


def test_hashtag_entity_type(db_session: Session) -> None:
    """Test that hashtags are created with correct entity type."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    contact.set_hashtags(["#test"])
    db_session.commit()
    db_session.refresh(contact)

    hashtag = db_session.query(Hashtag).filter_by(
        name="#test",
        entity_type=EntityType.CONTACT
    ).first()
    assert hashtag is not None
    assert hashtag.entity_type == EntityType.CONTACT


def test_hashtag_frequency_tracking(db_session: Session) -> None:
    """Test tracking frequency and staleness of contact hashtags."""
    # Create a contact with a weekly tag
    contact = Contact(name="John Doe")
    db_session.add(contact)
    contact.set_hashtags(["#weekly"])
    db_session.commit()

    # Get the weekly tag
    weekly_tag = contact.hashtags[0]

    # Set frequency and last contact
    weekly_tag.frequency_days = 7
    weekly_tag.last_contact = datetime.now(UTC)
    db_session.commit()

    # Tag should not be stale yet
    assert not weekly_tag.is_stale()

    # Move last_contact to 8 days ago
    weekly_tag.last_contact = datetime.now(UTC) - timedelta(days=8)
    db_session.commit()

    # Tag should now be stale
    assert weekly_tag.is_stale()
    assert weekly_tag.staleness_days == 1


def test_tag_frequency_configuration(db_session: Session) -> None:
    """Test configuring frequency tracking on a tag."""
    # Create a tag
    tag = Hashtag(name="#weekly", entity_type=EntityType.CONTACT)
    db_session.add(tag)
    db_session.commit()

    # Set frequency
    tag.frequency_days = 7
    assert tag.frequency_days == 7
    assert not tag.is_stale()  # No last_contact yet, so not stale
    assert tag.staleness_days is None  # No last_contact yet

    # Set last contact
    tag.last_contact = datetime.now(UTC)
    db_session.commit()
    assert not tag.is_stale()
    assert tag.staleness_days == 0


def test_tag_staleness_calculation(db_session: Session) -> None:
    """Test calculating tag staleness."""
    # Create a tag with weekly frequency
    tag = Hashtag(name="#weekly", entity_type=EntityType.CONTACT)
    tag.frequency_days = 7
    tag.last_contact = datetime.now(UTC) - timedelta(days=10)  # 10 days ago
    db_session.add(tag)
    db_session.commit()

    assert tag.is_stale()
    assert tag.staleness_days == 3  # 10 days - 7 days = 3 days overdue


def test_tag_frequency_inheritance(db_session: Session) -> None:
    """Test that new statements inherit tag frequency settings."""
    # Create a contact with a weekly tag
    contact = Contact(name="John Doe")
    db_session.add(contact)
    contact.set_hashtags(["#weekly"])
    db_session.commit()

    # Configure frequency on the tag
    weekly_tag = contact.hashtags[0]
    weekly_tag.frequency_days = 7
    weekly_tag.last_contact = datetime.now(UTC)
    db_session.commit()

    # When we create a statement (to be implemented)
    # It should inherit the same tag with the same frequency
    # But have its own last_contact tracking
    # TODO: Implement this part when we add Statement model


def test_multiple_tag_frequencies(db_session: Session) -> None:
    """Test handling multiple tags with different frequencies."""
    # Create a contact with multiple tags
    contact = Contact(name="John Doe")
    db_session.add(contact)
    contact.set_hashtags(["#weekly", "#monthly"])
    db_session.commit()

    # Set different frequencies
    weekly_tag = next(t for t in contact.hashtags if t.name == "#weekly")
    monthly_tag = next(t for t in contact.hashtags if t.name == "#monthly")

    weekly_tag.frequency_days = 7
    monthly_tag.frequency_days = 30

    now = datetime.now(UTC)
    weekly_tag.last_contact = now - timedelta(days=10)  # Overdue
    monthly_tag.last_contact = now - timedelta(days=20)  # Not overdue
    db_session.commit()

    assert weekly_tag.is_stale()
    assert not monthly_tag.is_stale()
    assert weekly_tag.staleness_days == 3
    assert monthly_tag.staleness_days == 0


def test_disable_tag_frequency(db_session: Session) -> None:
    """Test disabling frequency tracking on a tag."""
    # Create a tag with frequency
    tag = Hashtag(name="#weekly", entity_type=EntityType.CONTACT)
    tag.frequency_days = 7
    tag.last_contact = datetime.now(UTC) - timedelta(days=10)
    db_session.add(tag)
    db_session.commit()

    assert tag.is_stale()  # Should be stale initially

    # Disable frequency tracking
    tag.frequency_days = None
    db_session.commit()

    assert not tag.is_stale()  # Should not be stale when frequency disabled
    assert tag.staleness_days is None


def test_update_tag_last_contact(db_session: Session) -> None:
    """Test updating last contact date on a tag."""
    # Create a tag with frequency
    tag = Hashtag(name="#weekly", entity_type=EntityType.CONTACT)
    tag.frequency_days = 7
    tag.last_contact = datetime.now(UTC) - timedelta(days=10)
    db_session.add(tag)
    db_session.commit()

    assert tag.is_stale()  # Should be stale initially

    # Update last contact to now
    tag.last_contact = datetime.now(UTC)
    db_session.commit()

    assert not tag.is_stale()  # Should not be stale after update
    assert tag.staleness_days == 0
