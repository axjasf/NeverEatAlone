"""SQLAlchemy implementation of note repository."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.orm import Session, selectinload

from ..models.domain.note_model import Note
from ..models.domain.tag_model import EntityType
from .interfaces import NoteRepository
from ..models.orm.note_orm import NoteORM
from ..models.orm.statement_orm import StatementORM
from ..models.orm.tag_orm import TagORM


class SQLAlchemyNoteRepository(NoteRepository):
    """SQLAlchemy implementation of note persistence."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository.

        Args:
            session: SQLAlchemy session
        """
        self._session = session

    def save(self, note: Note) -> Note:
        """Save a note.

        Args:
            note: The note to save

        Returns:
            The saved note with any updates from the database
        """
        # Convert domain model to ORM
        note_orm = NoteORM(
            id=note.id,
            contact_id=note.contact_id,
            content=note.content,
            is_interaction=note.is_interaction,
            interaction_date=note.interaction_date,
        )

        # Merge to handle both insert and update
        note_orm = self._session.merge(note_orm)
        self._session.flush()

        # Add statements with tags
        # First, clear existing statements
        note_orm.statements = []
        self._session.flush()

        for i, statement in enumerate(note.statements):
            statement_orm = StatementORM(
                id=statement.id,
                content=statement.content,
                sequence_number=i,
                note_id=note_orm.id,
                created_at=statement.created_at,
                updated_at=statement.updated_at
            )
            statement_orm = self._session.merge(statement_orm)
            self._session.flush()

            # Store current timestamps to restore after setting tags
            current_created_at = statement_orm.created_at
            current_updated_at = statement_orm.updated_at

            # Add statement tags using set_tags
            statement_orm.set_tags([tag.name for tag in statement.tags])

            # Restore the original timestamps
            statement_orm.created_at = current_created_at
            statement_orm.updated_at = current_updated_at
            note_orm.statements.append(statement_orm)

        # Add note tags
        for tag in note.tags:
            tag_orm = TagORM(
                name=tag.name,
                entity_type=EntityType.NOTE.value,
                entity_id=note_orm.id
            )
            tag_orm = self._session.merge(tag_orm)
            note_orm.tags.append(tag_orm)

        self._session.flush()
        return self._to_domain(note_orm)

    def find_by_id(self, note_id: UUID) -> Optional[Note]:
        """Find a note by its ID.

        Args:
            note_id: The ID to search for

        Returns:
            The note if found, None otherwise
        """
        stmt = (
            select(NoteORM)
            .options(
                selectinload(NoteORM.statements),
                selectinload(NoteORM.tags),
            )
            .where(NoteORM.id == note_id)
        )
        note_orm = self._session.execute(stmt).unique().scalar_one_or_none()
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
        stmt = (
            select(NoteORM)
            .options(
                selectinload(NoteORM.statements),
                selectinload(NoteORM.tags),
            )
            .where(NoteORM.contact_id == contact_id)
        )
        notes_orm = self._session.execute(stmt).scalars().unique().all()
        return [self._to_domain(note) for note in notes_orm]

    def find_by_tag(self, tag_name: str) -> List[Note]:
        """Find all notes with a specific tag.

        Args:
            tag_name: The tag name to search for

        Returns:
            List of notes with the tag
        """
        stmt = (
            select(NoteORM)
            .options(
                selectinload(NoteORM.statements),
                selectinload(NoteORM.tags),
            )
            .join(NoteORM.tags)
            .where(and_(
                TagORM.name == tag_name,
                TagORM.entity_type == EntityType.NOTE.value
            ))
        )
        notes_orm = self._session.execute(stmt).scalars().unique().all()
        return [self._to_domain(note) for note in notes_orm]

    def find_interactions(self, contact_id: UUID) -> List[Note]:
        """Find all interaction notes for a contact.

        Args:
            contact_id: The contact's ID

        Returns:
            List of interaction notes for the contact, ordered by interaction_date DESC
        """
        stmt = (
            select(NoteORM)
            .options(
                selectinload(NoteORM.statements),
                selectinload(NoteORM.tags),
            )
            .where(and_(
                NoteORM.contact_id == contact_id,
                NoteORM.is_interaction == True,  # noqa: E712
            ))
            .order_by(NoteORM.interaction_date.desc())
        )
        notes_orm = self._session.execute(stmt).scalars().unique().all()
        return [self._to_domain(note) for note in notes_orm]

    def find_interactions_by_tag(self, tag_name: str) -> List[Note]:
        """Find all interaction notes with a specific tag.

        Args:
            tag_name: The tag name to search for

        Returns:
            List of interaction notes with the tag, ordered by interaction_date DESC
        """
        stmt = (
            select(NoteORM)
            .options(
                selectinload(NoteORM.statements),
                selectinload(NoteORM.tags),
            )
            .join(NoteORM.tags)
            .where(and_(
                NoteORM.is_interaction == True,  # noqa: E712
                TagORM.name == tag_name.lower(),
                TagORM.entity_type == EntityType.NOTE.value
            ))
            .order_by(NoteORM.interaction_date.desc())
        )
        notes_orm = self._session.execute(stmt).scalars().unique().all()
        return [self._to_domain(note) for note in notes_orm]

    def delete(self, note: Note) -> None:
        """Delete a note.

        Args:
            note: The note to delete
        """
        stmt = (
            select(NoteORM)
            .options(
                selectinload(NoteORM.statements),
                selectinload(NoteORM.tags),
            )
            .where(NoteORM.id == note.id)
        )
        note_orm = self._session.execute(stmt).unique().scalar_one_or_none()
        if note_orm:
            self._session.delete(note_orm)
            # Removed commit as per CR-2025.02-50
            # Transaction management should be handled by the service layer

    def _to_domain(self, note_orm: NoteORM) -> Note:
        """Convert ORM model to domain model.

        Args:
            note_orm: The ORM model to convert

        Returns:
            The domain model
        """
        try:
            note = Note(
                contact_id=note_orm.contact_id,
                content=note_orm.content,
                is_interaction=note_orm.is_interaction,
                interaction_date=note_orm.interaction_date,
            )
            note.id = note_orm.id
            note.created_at = note_orm.created_at
            note.updated_at = note_orm.updated_at

            # Add statements with their tags
            for statement_orm in note_orm.statements:
                statement = note.add_statement(statement_orm.content)
                statement.created_at = statement_orm.created_at
                statement.updated_at = statement_orm.updated_at
                # Add statement tags
                for tag_orm in statement_orm.tags:
                    statement.add_tag(tag_orm.name)

            # Add note tags
            for tag_orm in note_orm.tags:
                note.add_tag(tag_orm.name)

            return note
        except Exception as e:
            # Log the error and re-raise to maintain the interface contract
            # In a real application, we would use proper logging here
            print(f"Error converting note ORM to domain model: {e}")
            raise
