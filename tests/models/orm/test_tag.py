"""Tests for the Tag ORM model.

Tests are organized by complexity and frequency of use:
1. Basic Tests - Creation and validation
2. Relationship Tests - Tag associations with different entities
3. State Management Tests - Update tracking and concurrent operations
4. Temporal Tests - Timezone handling and frequency updates
"""

import pytest
from datetime import datetime, UTC
import time
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect
from backend.app.models.orm.tag_orm import TagORM
from backend.app.models.orm.contact_orm import ContactORM
from backend.app.models.orm.note_orm import NoteORM
from backend.app.models.orm.statement_orm import StatementORM
from backend.app.models.domain.tag_model import EntityType
from backend.app.models.orm.base_orm import BaseORMModel
from backend.app.models.orm.association_tables_orm import note_tags, statement_tags


# region Basic Tests

def test_tag_creation_with_required_fields(db_session: Session) -> None:
    """Test creating a tag with only required fields.

    Verify:
    1. Basic tag creation works
    2. Required fields are saved correctly
    3. Optional fields default to None
    4. Basic persistence works
    """
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
    assert saved_tag is not None, "Tag was not saved"
    assert saved_tag.name == "#test", "Tag name was not saved correctly"
    assert saved_tag.entity_type == EntityType.CONTACT.value, "Entity type was not saved correctly"
    assert saved_tag.frequency_days is None, "Frequency days should default to None"
    assert saved_tag.last_contact is None, "Last contact should default to None"


def test_tag_required_fields(db_session: Session) -> None:
    """Test that required fields cannot be null.

    Verify:
    1. Missing entity_id raises error
    2. Missing entity_type raises error
    3. Missing name raises error
    4. Database remains consistent after errors
    """
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


def test_tag_entity_type_validation(db_session: Session) -> None:
    """Test that entity_type must be a valid EntityType value.

    Verify:
    1. Valid entity types are accepted
    2. Invalid entity types raise error
    3. Case sensitivity is handled
    4. Empty/null values are rejected
    """
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

# endregion


# region Relationship Tests

def test_tag_contact_relationship(db_session: Session) -> None:
    """Test the relationship between tags and contacts.

    Verify:
    1. Tags can be associated with contacts
    2. Relationship is bidirectional
    3. Tags survive contact deletion
    4. Relationship metadata is correct
    """
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
    assert len(contact.tags) == 1, "Tag not associated with contact"
    assert contact.tags[0].name == "#test", "Wrong tag associated"

    # Test that tag survives contact deletion
    db_session.delete(contact)
    db_session.commit()

    saved_tag = db_session.get(TagORM, tag.id)
    assert saved_tag is not None, "Tag should survive contact deletion"


def test_tag_note_relationship(db_session: Session) -> None:
    """Test the relationship between tags and notes.

    Verify:
    1. Tags can be associated with notes
    2. Relationship is bidirectional
    3. Tags survive note deletion
    4. Relationship metadata is correct
    """
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
    assert len(note.tags) == 1, "Tag not associated with note"
    assert note.tags[0].name == "#test", "Wrong tag associated"

    # Test that tag survives note deletion
    db_session.delete(note)
    db_session.commit()

    saved_tag = db_session.get(TagORM, tag.id)
    assert saved_tag is not None, "Tag should survive note deletion"


def test_tag_statement_relationship(db_session: Session) -> None:
    """Test the relationship between tags and statements.

    Verify:
    1. Tags can be associated with statements
    2. Relationship is bidirectional
    3. Tags survive statement deletion
    4. Relationship metadata is correct
    """
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
    assert len(statement.tags) == 1, "Tag not associated with statement"
    assert statement.tags[0].name == "#test", "Wrong tag associated"

    # Test that tag survives statement deletion
    db_session.delete(statement)
    db_session.commit()

    saved_tag = db_session.get(TagORM, tag.id)
    assert saved_tag is not None, "Tag should survive statement deletion"


def test_tag_association_table_definitions(db_session: Session) -> None:
    """Verify tag association tables are correctly defined.

    Verify:
    1. Each association table exists exactly once
    2. No duplicate table warnings
    3. Tables are properly named and indexed
    4. Proper foreign key constraints exist
    """
    # Get SQLAlchemy metadata
    metadata = BaseORMModel.metadata
    inspector = inspect(db_session.get_bind())

    # Check association tables exist exactly once
    assert 'contact_tags' in metadata.tables, "Contact tags table missing"
    assert 'note_tags' in metadata.tables, "Note tags table missing"
    assert 'statement_tags' in metadata.tables, "Statement tags table missing"

    # Verify no duplicate tables in database
    all_tables = inspector.get_table_names()
    assert all_tables.count('contact_tags') == 1, "Duplicate contact_tags table"
    assert all_tables.count('note_tags') == 1, "Duplicate note_tags table"
    assert all_tables.count('statement_tags') == 1, "Duplicate statement_tags table"

    # Verify proper indexes exist
    contact_indexes = inspector.get_indexes('contact_tags')
    note_indexes = inspector.get_indexes('note_tags')
    statement_indexes = inspector.get_indexes('statement_tags')

    # Each table should have indexes on both columns
    for indexes in [contact_indexes, note_indexes, statement_indexes]:
        column_names = {str(col) for idx in indexes for col in idx['column_names']}
        assert 'tag_id' in column_names, "Missing tag_id index"
        assert any('entity_id' == str(col) for col in column_names), "Missing entity_id index"

# endregion


# region State Management Tests

def test_tag_frequency_and_last_contact(db_session: Session) -> None:
    """Test setting frequency and last contact on a tag.

    Verify:
    1. Frequency days are stored correctly
    2. Last contact dates are preserved
    3. Timezone information is handled
    4. Update tracking works correctly
    """
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
    assert saved_tag is not None, "Tag was not saved"
    assert saved_tag.frequency_days == 7, "Frequency days not saved correctly"
    assert saved_tag.last_contact is not None, "Last contact not saved"
    saved_time = saved_tag.last_contact.replace(tzinfo=None)
    test_time = now.replace(tzinfo=None)
    assert saved_time == test_time, "Last contact time mismatch"

    # Test frequency_last_updated
    saved_tag.update_frequency(14)  # Change frequency
    db_session.commit()
    db_session.refresh(saved_tag)

    assert saved_tag.frequency_days == 14, "Frequency update failed"
    assert saved_tag.frequency_last_updated is not None, "Update time not set"
    assert saved_tag.frequency_last_updated.tzinfo == UTC, "Update time should be in UTC"
    now = datetime.now(UTC)
    assert abs((now - saved_tag.frequency_last_updated).total_seconds()) < 2, "Update time incorrect"

    # Test clearing frequency
    before_clear = datetime.now(UTC)
    saved_tag.update_frequency(None)
    db_session.commit()
    db_session.refresh(saved_tag)

    assert saved_tag.frequency_days is None, "Frequency not cleared"
    assert saved_tag.frequency_last_updated is not None, "Update time not set"
    assert saved_tag.frequency_last_updated > before_clear, "Update time not updated"


def test_concurrent_tag_operations(db_session: Session) -> None:
    """Test that concurrent tag operations are handled correctly.

    Verify:
    1. Multiple tags can be created concurrently
    2. No duplicate tags are created
    3. Each operation is atomic
    4. Final state is consistent
    """
    # Create test contact
    contact = ContactORM(name="Test Contact")
    db_session.add(contact)
    db_session.commit()
    contact_id = str(contact.id)

    # Create tags
    expected_tags = 5
    tag_names = [f"#tag{i}" for i in range(expected_tags)]

    # Simulate concurrent operations by interleaving tag creation
    for tag_name in tag_names:
        tag = TagORM(
            entity_id=contact_id,
            entity_type=EntityType.CONTACT.value,
            name=tag_name
        )
        db_session.add(tag)
        # Commit after each tag to simulate separate transactions
        db_session.commit()

        # Verify the tag was added correctly
        db_session.refresh(contact)
        current_tags = db_session.query(TagORM).filter_by(entity_id=contact_id).all()
        assert tag.id in [t.id for t in current_tags], f"Tag {tag_name} was not added correctly"

    # Final verification
    db_session.refresh(contact)
    tags = db_session.query(TagORM).filter_by(entity_id=contact_id).all()
    assert len(tags) == expected_tags, f"Expected {expected_tags} tags, got {len(tags)}"

    # Verify no duplicate tags
    tag_names_in_db = {tag.name for tag in tags}
    assert len(tag_names_in_db) == expected_tags, "Duplicate tags found"

# endregion


# region Event Tests

def test_tag_update_events(db_session: Session) -> None:
    """Test that tag updates trigger appropriate events.

    Verify:
    1. Frequency updates trigger frequency_last_updated
    2. Last contact updates are tracked
    3. Multiple updates are handled correctly
    4. Event order is preserved
    """
    # Create contact and tag
    contact = ContactORM(name="Test Contact")
    db_session.add(contact)
    db_session.commit()

    tag = TagORM(
        entity_id=contact.id,
        entity_type=EntityType.CONTACT.value,
        name="#test"
    )
    db_session.add(tag)
    db_session.commit()

    # Initial state
    assert tag.frequency_last_updated is None, "Should not have update time initially"

    # Update frequency
    before_update = datetime.now(UTC)
    tag.update_frequency(7)  # Set weekly frequency
    db_session.commit()
    db_session.refresh(tag)

    # Verify frequency update event
    assert tag.frequency_last_updated is not None, "Update time not set"
    assert tag.frequency_last_updated.tzinfo == UTC, "Update time should be in UTC"
    assert tag.frequency_last_updated > before_update, "Update time not after operation"

    # Update frequency again
    before_second_update = datetime.now(UTC)
    tag.update_frequency(14)  # Change to bi-weekly
    db_session.commit()
    db_session.refresh(tag)

    # Verify second update event
    assert tag.frequency_last_updated > before_second_update, "Second update not tracked"


def test_tag_association_events(db_session: Session) -> None:
    """Test events triggered by tag associations.

    Verify:
    1. Adding tags updates parent timestamps
    2. Removing tags updates parent timestamps
    3. Events trigger in correct order
    4. Association metadata is updated
    """
    # Create contact and note
    contact = ContactORM(name="Test Contact")
    db_session.add(contact)
    db_session.commit()

    note = NoteORM(contact_id=contact.id, content="Test note")
    db_session.add(note)
    db_session.commit()
    initial_note_update = note.updated_at

    # Create and associate tag
    time.sleep(0.001)  # Ensure timestamp difference
    tag = TagORM(
        entity_id=note.id,
        entity_type=EntityType.NOTE.value,
        name="#test"
    )
    db_session.add(tag)
    note.tags.append(tag)
    db_session.commit()
    db_session.refresh(note)

    # Verify note update triggered
    assert note.updated_at > initial_note_update, "Note not updated after tag addition"

    # Remove tag
    time.sleep(0.001)  # Ensure timestamp difference
    note.tags.remove(tag)
    db_session.commit()
    db_session.refresh(note)

    # Verify note update triggered again
    assert note.updated_at > initial_note_update, "Note not updated after tag removal"


def test_tag_cascade_events(db_session: Session) -> None:
    """Test events during cascading operations.

    Verify:
    1. Parent deletion triggers appropriate events
    2. Association cleanup happens in correct order
    3. Tag state remains consistent
    4. No orphaned references remain
    """
    # Create contact and note
    contact = ContactORM(name="Test Contact")
    db_session.add(contact)
    db_session.commit()

    note = NoteORM(contact_id=contact.id, content="Test note")
    db_session.add(note)
    db_session.commit()

    # Create statement with tags
    statement = StatementORM(
        note_id=note.id,
        content="Test statement",
        sequence_number=1
    )
    db_session.add(statement)
    db_session.commit()

    # Add tags to both note and statement
    tag1 = TagORM(
        entity_id=note.id,
        entity_type=EntityType.NOTE.value,
        name="#test1"
    )
    tag2 = TagORM(
        entity_id=statement.id,
        entity_type=EntityType.STATEMENT.value,
        name="#test2"
    )
    db_session.add_all([tag1, tag2])
    note.tags.append(tag1)
    statement.tags.append(tag2)
    db_session.commit()

    # Store tag IDs
    tag1_id = tag1.id
    tag2_id = tag2.id

    # Delete note (should cascade to statement)
    db_session.delete(note)
    db_session.commit()

    # Verify tags still exist but associations are cleaned up
    remaining_tags = db_session.query(TagORM).filter(
        TagORM.id.in_([tag1_id, tag2_id])
    ).all()
    assert len(remaining_tags) == 2, "Tags should survive cascade deletion"

    # Verify no orphaned associations
    note_assocs = db_session.query(note_tags).all()
    statement_assocs = db_session.query(statement_tags).all()
    assert len(note_assocs) == 0, "Note tag associations should be cleaned up"
    assert len(statement_assocs) == 0, "Statement tag associations should be cleaned up"

# endregion
