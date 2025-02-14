"""Note domain model."""
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from uuid import UUID
from .base import BaseModel

if TYPE_CHECKING:
    from .tag import Tag


class Statement(BaseModel):
    """A single statement within a note.

    Statements allow breaking down notes into smaller, taggable pieces
    for more granular organization and tracking.
    """
    def __init__(self, content: str) -> None:
        """Create a new statement.

        Args:
            content: The statement text

        Raises:
            ValueError: If content is empty
        """
        super().__init__()
        if not content.strip():
            raise ValueError("Statement content cannot be empty")
        self.content = content.strip()
        self.tags: List["Tag"] = []

    def add_tag(self, tag_name: str) -> None:
        """Add a tag to the statement.

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
            tag = Tag(self.id, EntityType.STATEMENT, tag_name)
            self.tags.append(tag)
            self._update_timestamp()

    def remove_tag(self, tag: "Tag") -> None:
        """Remove a tag from the statement.

        Args:
            tag: The tag to remove
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self._update_timestamp()


class Note(BaseModel):
    """A note about a contact.

    Notes capture interactions, observations, and plans related to a contact.
    They can be broken down into statements and tagged for organization.
    """
    def __init__(self, contact_id: UUID, content: str) -> None:
        """Create a new note.

        Args:
            contact_id: ID of the contact this note is about
            content: The note content

        Raises:
            ValueError: If content is empty
        """
        super().__init__()
        if not content.strip():
            raise ValueError("Content cannot be empty")

        self.contact_id = contact_id
        self.content = content.strip()
        self.statements: List[Statement] = []
        self.tags: List["Tag"] = []

    def update_content(self, new_content: str) -> None:
        """Update the note's content.

        Args:
            new_content: New content for the note

        Raises:
            ValueError: If new_content is empty
        """
        if not new_content.strip():
            raise ValueError("Content cannot be empty")
        self.content = new_content.strip()
        self._update_timestamp()

    def add_statement(self, content: str) -> Statement:
        """Add a new statement to the note.

        Args:
            content: The statement content

        Returns:
            The created statement

        Raises:
            ValueError: If content is empty
        """
        statement = Statement(content)
        self.statements.append(statement)
        self._update_timestamp()
        return statement

    def remove_statement(self, statement: Statement) -> None:
        """Remove a statement from the note.

        Args:
            statement: The statement to remove
        """
        if statement in self.statements:
            self.statements.remove(statement)
            self._update_timestamp()

    def add_tag(self, tag_name: str) -> None:
        """Add a tag to the note.

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
            tag = Tag(self.id, EntityType.NOTE, tag_name)
            self.tags.append(tag)
            self._update_timestamp()

    def remove_tag(self, tag: "Tag") -> None:
        """Remove a tag from the note.

        Args:
            tag: The tag to remove
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self._update_timestamp()

    def _update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = datetime.now(timezone.utc)
