"""Repository interfaces for the application."""

from typing import Protocol, Optional, List
from uuid import UUID
from ..models.domain.note_model import Note
from ..models.domain.tag_model import Tag, EntityType
from ..models.domain.reminder_model import Reminder
from ..models.domain.template_model import Template
from ..models.domain.contact_model import Contact


class NoteRepository(Protocol):
    """Interface for note persistence operations."""

    def save(self, note: Note) -> Note:
        """Save a note.

        Args:
            note: The note to save

        Returns:
            The saved note with any updates from the database
        """
        ...

    def find_by_id(self, note_id: UUID) -> Optional[Note]:
        """Find a note by its ID.

        Args:
            note_id: The ID to search for

        Returns:
            The note if found, None otherwise
        """
        ...

    def find_by_contact(self, contact_id: UUID) -> List[Note]:
        """Find all notes for a contact.

        Args:
            contact_id: The contact's ID

        Returns:
            List of notes for the contact
        """
        ...

    def find_by_tag(self, tag_name: str) -> List[Note]:
        """Find all notes with a specific tag.

        Args:
            tag_name: The tag name to search for

        Returns:
            List of notes with the tag
        """
        ...

    def delete(self, note: Note) -> None:
        """Delete a note.

        Args:
            note: The note to delete
        """
        ...


class TagRepository(Protocol):
    """Interface for tag persistence operations."""

    def save(self, tag: Tag) -> Tag:
        """Save a tag.

        Args:
            tag: The tag to save

        Returns:
            The saved tag with any updates from the database
        """
        ...

    def find_by_id(self, tag_id: UUID) -> Optional[Tag]:
        """Find a tag by its ID.

        Args:
            tag_id: The ID to search for

        Returns:
            The tag if found, None otherwise
        """
        ...

    def find_by_entity(self, entity_id: UUID, entity_type: EntityType) -> List[Tag]:
        """Find all tags for an entity.

        Args:
            entity_id: The entity's ID
            entity_type: The type of entity

        Returns:
            List of tags for the entity
        """
        ...

    def find_by_name(self, name: str) -> List[Tag]:
        """Find all tags with a specific name.

        Args:
            name: The tag name to search for

        Returns:
            List of tags with the name
        """
        ...

    def find_stale(self) -> List[Tag]:
        """Find all tags that are stale based on their frequency.

        Returns:
            List of stale tags
        """
        ...

    def delete(self, tag: Tag) -> None:
        """Delete a tag.

        Args:
            tag: The tag to delete
        """
        ...


class ReminderRepository(Protocol):
    """Interface for reminder persistence operations."""

    def save(self, reminder: Reminder) -> Reminder:
        """Save a reminder.

        Args:
            reminder: The reminder to save

        Returns:
            The saved reminder with any updates from the database
        """
        ...

    def find_by_id(self, reminder_id: UUID) -> Optional[Reminder]:
        """Find a reminder by its ID.

        Args:
            reminder_id: The ID to search for

        Returns:
            The reminder if found, None otherwise
        """
        ...

    def find_by_contact(self, contact_id: UUID) -> List[Reminder]:
        """Find all reminders for a contact.

        Args:
            contact_id: The contact's ID

        Returns:
            List of reminders for the contact
        """
        ...

    def find_by_note(self, note_id: UUID) -> List[Reminder]:
        """Find all reminders linked to a note.

        Args:
            note_id: The note's ID

        Returns:
            List of reminders linked to the note
        """
        ...

    def find_pending(self) -> List[Reminder]:
        """Find all pending reminders.

        Returns:
            List of reminders in PENDING status
        """
        ...

    def find_overdue(self) -> List[Reminder]:
        """Find all overdue reminders.

        Returns:
            List of reminders past their due date
        """
        ...

    def delete(self, reminder: Reminder) -> None:
        """Delete a reminder.

        Args:
            reminder: The reminder to delete
        """
        ...


class ContactRepository(Protocol):
    """Interface for contact persistence."""

    def save(self, contact: Contact) -> Contact:
        """Save a contact."""
        ...

    def find_by_id(self, contact_id: UUID) -> Optional[Contact]:
        """Find a contact by ID."""
        ...

    def find_by_tag(self, tag_name: str) -> List[Contact]:
        """Find contacts by tag name."""
        ...

    def find_stale(self) -> List[Contact]:
        """Find contacts with stale tags."""
        ...

    def delete(self, contact: Contact) -> None:
        """Delete a contact."""
        ...

    def find_all(self) -> List[Contact]:
        """Find all contacts."""
        ...


class TemplateRepository(Protocol):
    """Interface for template persistence."""

    def save(self, template: Template) -> None:
        """Save a template.

        Args:
            template: The template to save
        """
        ...

    def get_by_id(self, template_id: UUID) -> Optional[Template]:
        """Get a template by its ID.

        Args:
            template_id: UUID of the template to find

        Returns:
            Template if found, None if not found

        Raises:
            ValueError: If template_id is invalid
        """
        ...

    def get_version(self, template_id: UUID, version: int) -> Optional[Template]:
        """Get a specific version of a template.

        Args:
            template_id: UUID of the template
            version: Version number to retrieve

        Returns:
            Template if found, None if not found

        Raises:
            ValueError: If template_id or version is invalid
        """
        ...

    def get_versions(self, template_id: UUID) -> List[Template]:
        """Get all versions of a template.

        Args:
            template_id: UUID of the template

        Returns:
            List of all versions of the template, ordered by version number

        Raises:
            ValueError: If template_id is invalid
        """
        ...
