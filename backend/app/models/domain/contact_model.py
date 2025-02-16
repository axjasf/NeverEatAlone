"""Contact domain model."""

from typing import Dict, Any, List, TYPE_CHECKING, Optional
from datetime import datetime
from .base_model import BaseModel

if TYPE_CHECKING:
    from .note_model import Note
    from .tag_model import Tag


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
        last_contact: When this contact was last contacted
        contact_briefing_text: A brief text about the last contact
    """

    def __init__(
        self,
        name: str,
        first_name: str | None = None,
        briefing_text: str | None = None,
        sub_information: Dict[str, Any] | None = None,
        last_contact: Optional[datetime] = None,
        contact_briefing_text: Optional[str] = None,
    ) -> None:
        """Initialize a new Contact.

        Args:
            name: The contact's name
            first_name: The contact's first name (optional)
            briefing_text: A brief description of the contact (optional)
            sub_information: Additional information about the contact (optional)
            last_contact: When this contact was last contacted (optional)
            contact_briefing_text: A brief text about the last contact (optional)

        Raises:
            ValueError: If sub_information is provided but not a dictionary
        """
        super().__init__()
        self.name = name
        self.first_name = first_name
        self.briefing_text = briefing_text

        # Validate sub_information is a dict if provided
        if sub_information is not None and not hasattr(sub_information, "items"):
            raise ValueError("sub_information must be a dictionary")
        self.sub_information = sub_information or {}

        self.last_contact = last_contact
        self.contact_briefing_text = contact_briefing_text
        self.notes: List["Note"] = []
        self.tags: List["Tag"] = []

    @property
    def hashtag_names(self) -> List[str]:
        """Get the list of hashtag names associated with this contact.

        Returns:
            List of hashtag names
        """
        return [tag.name for tag in self.tags]

    def set_hashtags(self, hashtags: List[str]) -> None:
        """Set the hashtags for this contact.

        This will remove any existing tags and add the new ones.

        Args:
            hashtags: List of hashtag names (must start with #)

        Raises:
            ValueError: If any hashtag doesn't start with #
        """
        # Clear existing tags
        self.tags.clear()

        # Add new tags
        for tag_name in hashtags:
            self.add_tag(tag_name)

        self._update_timestamp()

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
        from .tag_model import Tag, EntityType

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
        from .note_model import Note

        note = Note(self.id, content)
        self.notes.append(note)
        self._update_timestamp()
        return note

    def add_interaction(
        self,
        interaction_date: Optional[datetime] = None,
        content: Optional[str] = None
    ) -> "Note":
        """Record an interaction with this contact.

        Args:
            interaction_date: When the interaction occurred
            content: Optional description of the interaction

        Returns:
            The created interaction note

        Raises:
            ValueError: If validation fails:
                - interaction_date is required
                - interaction_date cannot be in future
                - content cannot be empty if provided
        """
        # Import here to avoid circular dependency
        from .note_model import Note

        # Create the interaction note
        note = Note(
            contact_id=self.id,
            content=content,
            is_interaction=True,
            interaction_date=interaction_date
        )

        # Update contact tracking
        self.last_contact = interaction_date
        if content:
            self.contact_briefing_text = content

        # Update all contact tags
        for tag in self.tags:
            tag.handle_note_interaction(True, interaction_date)

        # Add note to contact
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
