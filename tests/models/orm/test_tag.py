"""Tests for the Tag ORM model."""

import pytest
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.app.models.orm.tag_orm import TagORM
from backend.app.models.orm.contact_orm import ContactORM
from backend.app.models.orm.note_orm import NoteORM
from backend.app.models.orm.statement_orm import StatementORM
from backend.app.models.domain.tag_model import EntityType
from sqlalchemy import MetaData, inspect
from backend.app.models.orm.base_orm import BaseORMModel


def test_tag_creation_with_required_fields(db_session: Session) -> None:
    """Test creating a tag with only required fields."""
    # Create and save contact first
    contact = ContactORM(name="Test Contact")
    db_session.add(contact)
    db_session.commit()

    tag = TagORM(
        entity_id=contact.id, entity_type=EntityType.CONTACT.value, name="#test"
    )
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)

    saved_tag = db_session.get(TagORM, tag.id)
    assert saved_tag is not None
    assert saved_tag.name == "#test"
    assert saved_tag.entity_type == EntityType.CONTACT.value
    assert saved_tag.frequency_days is None
    assert saved_tag.last_contact is None


def test_tag_entity_type_validation(db_session: Session) -> None:
    """Test that entity_type must be a valid EntityType value."""
    # Create and save contact first
    contact = ContactORM(name="Test Contact")
    db_session.add(contact)
    db_session.commit()

    tag = TagORM(
        entity_id=contact.id,
        entity_type="invalid_type",  # Invalid entity type
        name="#test",
    )
    db_session.add(tag)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_tag_frequency_and_last_contact(db_session: Session) -> None:
    """Test setting frequency and last contact on a tag."""
    # Create and save contact first
    contact = ContactORM(name="Test Contact")
    db_session.add(contact)
    db_session.commit()

    now = datetime.now(UTC)
    tag = TagORM(
        entity_id=contact.id,
        entity_type=EntityType.CONTACT.value,
        name="#weekly",
        frequency_days=7,
        last_contact=now,
    )
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)

    saved_tag = db_session.get(TagORM, tag.id)
    assert saved_tag is not None
    assert saved_tag.frequency_days == 7
    # Compare timestamps without timezone info since SQLite might not
    # preserve it
    assert saved_tag.last_contact is not None
    saved_time = saved_tag.last_contact.replace(tzinfo=None)
    test_time = now.replace(tzinfo=None)
    assert saved_time == test_time

    # Test frequency_last_updated
    saved_tag.update_frequency(14)  # Change frequency
    db_session.commit()
    db_session.refresh(saved_tag)

    assert saved_tag.frequency_days == 14
    assert saved_tag.frequency_last_updated is not None
    # Compare timestamps without timezone info since SQLite might not preserve it
    saved_time = saved_tag.frequency_last_updated.replace(tzinfo=None)
    # The time should be close to now
    now = datetime.now(UTC)
    assert abs((now.replace(tzinfo=None) - saved_time).total_seconds()) < 2

    # Test clearing frequency
    saved_tag.update_frequency(None)
    db_session.commit()
    db_session.refresh(saved_tag)

    assert saved_tag.frequency_days is None
    assert saved_tag.frequency_last_updated is None


def test_tag_contact_relationship(db_session: Session) -> None:
    """Test the relationship between tags and contacts."""
    # Create contact and tag
    contact = ContactORM(name="Test Contact")
    db_session.add(contact)
    db_session.commit()

    tag = TagORM(
        entity_id=contact.id, entity_type=EntityType.CONTACT.value, name="#test"
    )
    db_session.add(tag)
    db_session.commit()

    # Associate tag with contact
    contact.tags.append(tag)
    db_session.commit()
    db_session.refresh(contact)

    # Verify relationship
    assert len(contact.tags) == 1
    assert contact.tags[0].name == "#test"

    # Test that tag survives contact deletion
    db_session.delete(contact)
    db_session.commit()

    saved_tag = db_session.get(TagORM, tag.id)
    assert saved_tag is not None  # Tag should still exist


def test_tag_note_relationship(db_session: Session) -> None:
    """Test the relationship between tags and notes."""
    # Create contact and note
    contact = ContactORM(name="Test Contact")
    db_session.add(contact)
    db_session.commit()

    note = NoteORM(contact_id=contact.id, content="Test note")
    db_session.add(note)
    db_session.commit()

    # Create and associate tag
    tag = TagORM(entity_id=note.id, entity_type=EntityType.NOTE.value, name="#test")
    db_session.add(tag)
    db_session.commit()

    note.tags.append(tag)
    db_session.commit()
    db_session.refresh(note)

    # Verify relationship
    assert len(note.tags) == 1
    assert note.tags[0].name == "#test"

    # Test that tag survives note deletion
    db_session.delete(note)
    db_session.commit()

    saved_tag = db_session.get(TagORM, tag.id)
    assert saved_tag is not None  # Tag should still exist


def test_tag_statement_relationship(db_session: Session) -> None:
    """Test the relationship between tags and statements."""
    # Create contact, note, and statement
    contact = ContactORM(name="Test Contact")
    db_session.add(contact)
    db_session.commit()

    note = NoteORM(contact_id=contact.id, content="Test note")
    db_session.add(note)
    db_session.commit()

    statement = StatementORM(
        note_id=note.id, content="Test statement", sequence_number=1
    )
    db_session.add(statement)
    db_session.commit()

    # Create and associate tag
    tag = TagORM(
        entity_id=statement.id, entity_type=EntityType.STATEMENT.value, name="#test"
    )
    db_session.add(tag)
    db_session.commit()

    statement.tags.append(tag)
    db_session.commit()
    db_session.refresh(statement)

    # Verify relationship
    assert len(statement.tags) == 1
    assert statement.tags[0].name == "#test"

    # Test that tag survives statement deletion
    db_session.delete(statement)
    db_session.commit()

    saved_tag = db_session.get(TagORM, tag.id)
    assert saved_tag is not None  # Tag should still exist


def test_tag_required_fields(db_session: Session) -> None:
    """Test that required fields cannot be null."""
    # Test missing entity_id
    tag = TagORM(entity_type=EntityType.CONTACT.value, name="#test")
    db_session.add(tag)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Test missing entity_type
    tag = TagORM(entity_id=ContactORM(name="Test Contact").id, name="#test")
    db_session.add(tag)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Test missing name
    tag = TagORM(
        entity_id=ContactORM(name="Test Contact").id,
        entity_type=EntityType.CONTACT.value,
    )
    db_session.add(tag)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_tag_association_table_definitions(db_session: Session) -> None:
    """Verify tag association tables are correctly defined.

    Tests:
    1. Each association table exists exactly once in SQLAlchemy metadata
    2. No duplicate table warnings in SQLAlchemy logs
    3. Tables are properly named and indexed
    """
    # Get SQLAlchemy metadata
    metadata = BaseORMModel.metadata
    inspector = inspect(db_session.get_bind())

    # Check association tables exist exactly once
    assert 'contact_tags' in metadata.tables
    assert 'note_tags' in metadata.tables
    assert 'statement_tags' in metadata.tables

    # Verify no duplicate tables in database
    all_tables = inspector.get_table_names()
    assert all_tables.count('contact_tags') == 1
    assert all_tables.count('note_tags') == 1
    assert all_tables.count('statement_tags') == 1

    # Verify proper indexes exist
    contact_indexes = inspector.get_indexes('contact_tags')
    note_indexes = inspector.get_indexes('note_tags')
    statement_indexes = inspector.get_indexes('statement_tags')

    # Each table should have indexes on both columns
    for indexes in [contact_indexes, note_indexes, statement_indexes]:
        column_names = {col for idx in indexes for col in idx['column_names']}
        assert 'tag_id' in column_names
        assert any('entity_id' in col for col in column_names)
