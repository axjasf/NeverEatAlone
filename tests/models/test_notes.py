import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.app.models.contact import Contact, EntityType
from backend.app.models.note import Note, Statement


def test_note_creation_with_required_fields(db_session: Session) -> None:
    """Test creating a note with only required fields."""
    # Create a contact first
    contact = Contact(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    # Create note
    note = Note(
        contact_id=contact.id,
        content="Had a great meeting today."
    )
    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)

    # Verify note
    saved_note = db_session.get(Note, note.id)
    assert saved_note is not None
    assert saved_note.content == "Had a great meeting today."
    assert saved_note.contact_id == contact.id
    assert saved_note.created_at is not None
    assert saved_note.statements == []  # No statements yet
    assert saved_note.tags == []  # No tags yet


def test_note_requires_contact(db_session: Session) -> None:
    """Test that notes must be associated with a contact."""
    note = Note(content="Test note")
    db_session.add(note)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_note_requires_content(db_session: Session) -> None:
    """Test that notes must have content."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    note = Note(contact_id=contact.id)  # type: ignore
    db_session.add(note)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_note_statement_creation(db_session: Session) -> None:
    """Test creating statements from a note."""
    # Create contact and note
    contact = Contact(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    note = Note(
        contact_id=contact.id,
        content="Had a great meeting today. Discussed project timeline. Need to follow up next week."
    )
    db_session.add(note)
    db_session.commit()

    # Create statements
    statements = [
        Statement(note_id=note.id, content="Had a great meeting today."),
        Statement(note_id=note.id, content="Discussed project timeline."),
        Statement(note_id=note.id, content="Need to follow up next week.")
    ]
    for stmt in statements:
        db_session.add(stmt)
    db_session.commit()
    db_session.refresh(note)

    # Verify statements
    assert len(note.statements) == 3
    assert [s.content for s in note.statements] == [
        "Had a great meeting today.",
        "Discussed project timeline.",
        "Need to follow up next week."
    ]


def test_note_statement_deletion(db_session: Session) -> None:
    """Test that deleting a note also deletes its statements."""
    # Create contact and note with statements
    contact = Contact(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    note = Note(
        contact_id=contact.id,
        content="Statement 1. Statement 2."
    )
    db_session.add(note)
    db_session.commit()

    statements = [
        Statement(note_id=note.id, content="Statement 1."),
        Statement(note_id=note.id, content="Statement 2.")
    ]
    for stmt in statements:
        db_session.add(stmt)
    db_session.commit()

    # Delete note
    db_session.delete(note)
    db_session.commit()

    # Verify statements are deleted
    remaining_statements = db_session.query(Statement).filter_by(note_id=note.id).all()
    assert len(remaining_statements) == 0


def test_note_tagging(db_session: Session) -> None:
    """Test adding tags to a note."""
    # Create contact and note
    contact = Contact(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    note = Note(
        contact_id=contact.id,
        content="Meeting about #project timeline."
    )
    db_session.add(note)
    db_session.commit()

    # Add tags to note
    note.set_tags(["#meeting", "#project"])
    db_session.commit()
    db_session.refresh(note)

    # Verify tags
    assert len(note.tags) == 2
    assert sorted(t.name for t in note.tags) == ["#meeting", "#project"]


def test_statement_tagging(db_session: Session) -> None:
    """Test adding tags to individual statements."""
    # Create contact and note with statement
    contact = Contact(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    note = Note(
        contact_id=contact.id,
        content="Meeting about project timeline."
    )
    db_session.add(note)
    db_session.commit()

    statement = Statement(
        note_id=note.id,
        content="Meeting about project timeline."
    )
    db_session.add(statement)
    db_session.commit()

    # Add tags to statement
    statement.set_tags(["#meeting", "#project"])
    db_session.commit()
    db_session.refresh(statement)

    # Verify tags
    assert len(statement.tags) == 2
    assert sorted(t.name for t in statement.tags) == ["#meeting", "#project"]
