import pytest
from datetime import datetime, UTC
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
    assert saved_contact.last_contact is None
    assert saved_contact.sub_information == {}
    assert saved_contact.hashtag_names == []


def test_contact_creation_with_all_fields(db_session: Session) -> None:
    """Test creating a contact with all available fields."""
    sub_info = {"family_status": "Married", "professional_situation": "CEO"}
    hashtags = ["#business", "#vip"]
    now = datetime.now(UTC)

    contact = Contact(name="John Doe")
    contact.first_name = "John"
    contact.contact_briefing_text = "Important business contact"
    contact.last_contact = now
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
    assert saved_contact.last_contact == now
    assert saved_contact.sub_information == sub_info
    assert saved_contact.hashtag_names == hashtags


def test_contact_update_last_contact(db_session: Session) -> None:
    """Test updating the last_contact field."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    now = datetime.now(UTC)
    contact.last_contact = now
    db_session.commit()
    db_session.refresh(contact)

    saved_contact = db_session.get(Contact, contact.id)
    assert saved_contact is not None
    assert saved_contact.last_contact == now


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
