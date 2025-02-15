"""SQLAlchemy implementation of note repository."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.domain.note import Note
from ..models.domain.tag import EntityType
from .interfaces import NoteRepository
from ..models.orm.note import NoteORM
from ..models.orm.statement import StatementORM
from ..models.orm.tag import TagORM


class SQLAlchemyNoteRepository(NoteRepository):
    """SQLAlchemy implementation of note persistence."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository.

        Args:
            session: SQLAlchemy session
        """
        self.session = session

    def save(self, note: Note) -> Note:
        """Save a note.

        Args:
            note: The note to save

        Returns:
            The saved note with any updates from the database
        """
        # Convert domain model to ORM
        note_orm = NoteORM(id=note.id, contact_id=note.contact_id, content=note.content)

        # Add statements
        for i, statement in enumerate(note.statements):
            statement_orm = StatementORM(content=statement.content, sequence_number=i)
            note_orm.statements.append(statement_orm)

            # Add statement tags
            for tag in statement.tags:
                tag_orm = TagORM(
                    name=tag.name,
                    entity_type=EntityType.STATEMENT.value,
                    entity_id=statement_orm.id,
                )
                statement_orm.tags.append(tag_orm)

        # Add note tags
        for tag in note.tags:
            tag_orm = TagORM(
                name=tag.name, entity_type=EntityType.NOTE.value, entity_id=note_orm.id
            )
            note_orm.tags.append(tag_orm)

        self.session.add(note_orm)
        self.session.commit()

        # Return the saved note
        return self._to_domain(note_orm)

    def find_by_id(self, note_id: UUID) -> Optional[Note]:
        """Find a note by its ID.

        Args:
            note_id: The ID to search for

        Returns:
            The note if found, None otherwise
        """
        note_orm = self.session.get(NoteORM, note_id)
        if not note_orm:
            return None
        return self._to_domain(note_orm)

    def find_by_contact(self, contact_id: UUID) -> List[Note]:
        """Find all notes for a contact.

        Args:
            contact_id: The contact's ID

        Returns:
            List of notes for the contact
        """
        stmt = select(NoteORM).where(NoteORM.contact_id == contact_id)
        notes_orm = self.session.execute(stmt).scalars().unique().all()
        return [self._to_domain(note) for note in notes_orm]

    def find_by_tag(self, tag_name: str) -> List[Note]:
        """Find all notes with a specific tag.

        Args:
            tag_name: The tag name to search for

        Returns:
            List of notes with the tag
        """
        stmt = select(NoteORM).join(NoteORM.tags).where(TagORM.name == tag_name.lower())
        notes_orm = self.session.execute(stmt).scalars().unique().all()
        return [self._to_domain(note) for note in notes_orm]

    def delete(self, note: Note) -> None:
        """Delete a note.

        Args:
            note: The note to delete
        """
        note_orm = self.session.get(NoteORM, note.id)
        if note_orm:
            self.session.delete(note_orm)
            self.session.commit()

    def _to_domain(self, note_orm: NoteORM) -> Note:
        """Convert ORM model to domain model.

        Args:
            note_orm: The ORM model to convert

        Returns:
            The domain model
        """
        # Create domain model
        note = Note(contact_id=note_orm.contact_id, content=note_orm.content)

        # Add statements
        for statement_orm in note_orm.statements:
            statement = note.add_statement(statement_orm.content)
            # Add statement tags
            for tag_orm in statement_orm.tags:
                statement.add_tag(tag_orm.name)

        # Add note tags
        for tag_orm in note_orm.tags:
            note.add_tag(tag_orm.name)

        return note
