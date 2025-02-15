"""Tests for the Note repository."""

from datetime import datetime, UTC
from uuid import uuid4
from sqlalchemy.orm import Session
from backend.app.models.domain.note_model import Note
from backend.app.repositories.sqlalchemy_note_repository import (
    SQLAlchemyNoteRepository,
)


TEST_UUID = uuid4()


def test_note_save_and_find(db_session: Session) -> None:
    """Test saving and finding a note."""
    repo = SQLAlchemyNoteRepository(db_session)

    # Create and save a note
    note = Note(contact_id=TEST_UUID, content="Test note content")
    repo.save(note)

    # Find by ID
    found = repo.find_by_id(note.id)
    assert found is not None
    assert found.contact_id == TEST_UUID
    assert found.content == "Test note content"


def test_note_find_by_contact(db_session: Session) -> None:
    """Test finding notes by contact."""
    repo = SQLAlchemyNoteRepository(db_session)

    # Create notes for different contacts
    note1 = Note(contact_id=TEST_UUID, content="Note 1")
    note2 = Note(contact_id=TEST_UUID, content="Note 2")
    note3 = Note(
        contact_id=uuid4(), content="Note 3"
    )
    repo.save(note1)
    repo.save(note2)
    repo.save(note3)

    # Find by contact
    notes = repo.find_by_contact(TEST_UUID)
    assert len(notes) == 2
    assert {n.content for n in notes} == {"Note 1", "Note 2"}


def test_note_find_by_tag(db_session: Session) -> None:
    """Test finding notes by tag."""
    repo = SQLAlchemyNoteRepository(db_session)

    # Create notes with tags
    note1 = Note(contact_id=TEST_UUID, content="Note 1")
    note1.add_tag("#test")
    note1.add_tag("#project")
    repo.save(note1)

    note2 = Note(contact_id=TEST_UUID, content="Note 2")
    note2.add_tag("#test")
    repo.save(note2)

    note3 = Note(contact_id=TEST_UUID, content="Note 3")
    note3.add_tag("#other")
    repo.save(note3)

    # Find by tag
    test_notes = repo.find_by_tag("#test")
    assert len(test_notes) == 2
    assert {n.content for n in test_notes} == {"Note 1", "Note 2"}

    project_notes = repo.find_by_tag("#project")
    assert len(project_notes) == 1
    assert project_notes[0].content == "Note 1"

    other_notes = repo.find_by_tag("#other")
    assert len(other_notes) == 1
    assert other_notes[0].content == "Note 3"


def test_note_with_statements(db_session: Session) -> None:
    """Test saving and finding notes with statements."""
    repo = SQLAlchemyNoteRepository(db_session)

    # Create note with statements
    note = Note(contact_id=TEST_UUID, content="Main note")
    note.add_statement("First statement")
    note.add_statement("Second statement")
    repo.save(note)

    # Find and verify statements
    found = repo.find_by_id(note.id)
    assert found is not None
    assert len(found.statements) == 2
    assert [s.content for s in found.statements] == [
        "First statement",
        "Second statement",
    ]


def test_note_with_statement_tags(db_session: Session) -> None:
    """Test saving and finding notes with tagged statements."""
    repo = SQLAlchemyNoteRepository(db_session)

    # Create note with tagged statements
    note = Note(contact_id=TEST_UUID, content="Main note")
    note.add_statement("First statement")
    note.add_statement("Second statement")
    repo.save(note)

    # Find and verify statements
    found = repo.find_by_id(note.id)
    assert found is not None
    assert len(found.statements) == 2
    assert found.statements[0].content == "First statement"
    assert found.statements[1].content == "Second statement"


def test_note_delete(db_session: Session) -> None:
    """Test deleting a note."""
    repo = SQLAlchemyNoteRepository(db_session)

    # Create note with statements and tags
    note = Note(contact_id=TEST_UUID, content="Test note")
    note.add_tag("#test")
    note.add_statement("Test statement")
    repo.save(note)

    # Verify note exists
    found = repo.find_by_id(note.id)
    assert found is not None

    # Delete note
    repo.delete(note)

    # Verify note is gone
    found = repo.find_by_id(note.id)
    assert found is None
