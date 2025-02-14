"""Contact domain model."""

from typing import Dict, Any, List, TYPE_CHECKING
from .base import BaseModel

if TYPE_CHECKING:
    from .note import Note
    from .tag import Tag


class Contact(BaseModel):
    """A contact represents a person or entity that we want to keep in
    touch with.

    Each contact can have basic information like name and additional data
    stored in a flexible JSON structure.

    Attributes:
        name: The contact's name
        first_name: The contact's first name
        briefing_text: A brief description of the contact
        sub_information: Additional information about the contact
        notes: Notes about this contact
        tags: Tags associated with this contact
    """

    def __init__(
        self,
        name: str,
        first_name: str | None = None,
        briefing_text: str | None = None,
        sub_information: Dict[str, Any] | None = None,
    ) -> None:
        """Initialize a new Contact.

        Args:
            name: The contact's name
            first_name: The contact's first name (optional)
            briefing_text: A brief description of the contact (optional)
            sub_information: Additional information about the contact
                (optional)

        Raises:
            ValueError: If sub_information is provided but not a dictionary
        """
        super().__init__()
        self.name = name
        self.first_name = first_name
        self.briefing_text = briefing_text
        if sub_information is not None and not isinstance(sub_information, dict):
            raise ValueError("sub_information must be a dictionary")
        self.sub_information = sub_information or {}
        self.notes: List["Note"] = []
        self.tags: List["Tag"] = []

    def add_tag(self, tag_name: str) -> None:
        """Add a tag to the contact.

        Args:
            tag_name: Name of the tag (must start with #)

        Raises:
            ValueError: If tag_name doesn't start with #
        """
        if not tag_name.startswith("#"):
            raise ValueError("Tag must start with #")

        # Import here to avoid circular dependency
        from .tag import Tag, EntityType

        tag_name = tag_name.lower()
        # Check if tag already exists
        if not any(t.name == tag_name for t in self.tags):
            tag = Tag(self.id, EntityType.CONTACT, tag_name)
            self.tags.append(tag)
            self._update_timestamp()

    def remove_tag(self, tag: "Tag") -> None:
        """Remove a tag from the contact.

        Args:
            tag: The tag to remove
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self._update_timestamp()

    def add_note(self, content: str) -> "Note":
        """Add a note about this contact.

        Args:
            content: The note content

        Returns:
            The created note
        """
        # Import here to avoid circular dependency
        from .note import Note

        note = Note(self.id, content)
        self.notes.append(note)
        self._update_timestamp()
        return note

    def remove_note(self, note: "Note") -> None:
        """Remove a note about this contact.

        Args:
            note: The note to remove
        """
        if note in self.notes:
            self.notes.remove(note)
            self._update_timestamp()
