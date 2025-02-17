"""Note domain model."""

from datetime import datetime, timezone, UTC
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID
from .base_model import BaseModel

if TYPE_CHECKING:
    from .tag_model import Tag


class Statement(BaseModel):
    """A single statement within a note.

    Statements allow breaking down notes into smaller, taggable pieces
    for more granular organization and tracking. The order of statements
    within a note is maintained through their position in the note's
    statements list, providing a natural and intuitive representation
    of how statements appear in a note.

    While the persistence layer (ORM) uses a sequence_number field to maintain
    this order in the database, the domain model intentionally abstracts this
    implementation detail away to maintain a clean separation of concerns.
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
        from .tag_model import Tag, EntityType

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

    Notes can be either:
    1. Content notes: Containing actual information about the contact
    2. Interaction records: Just tracking that contact happened

    For content notes:
    - content is required
    - interaction_date must be None

    For interaction notes:
    - interaction_date is required (must be timezone-aware, stored in UTC)
    - content is optional

    All datetime fields are stored in UTC internally.
    """

    def __init__(
        self,
        contact_id: UUID,
        content: Optional[str] = None,
        is_interaction: bool = False,
        interaction_date: Optional[datetime] = None
    ) -> None:
        """Create a new note.

        Args:
            contact_id: ID of the contact this note is about
            content: The note content (required for non-interaction notes)
            is_interaction: Whether this note represents an interaction
            interaction_date: When the interaction occurred (required for interaction notes)
                           Must be timezone-aware, will be stored in UTC

        Raises:
            ValueError: If validation fails:
                - Content notes require content
                - Interaction notes require date
                - Content notes cannot have interaction date
                - Interaction date cannot be in future
                - Interaction date must be timezone-aware
        """
        super().__init__()

        # Validate interaction rules
        if is_interaction:
            if not interaction_date:
                raise ValueError("Interaction notes require a date")

            # Ensure timezone awareness
            if interaction_date.tzinfo is None:
                raise ValueError("Interaction date must be timezone-aware")

            # Convert to UTC for storage
            utc_date = interaction_date.astimezone(UTC)

            # Validate not in future
            if utc_date > datetime.now(UTC):
                raise ValueError("Interaction date cannot be in the future")

            # Store in UTC
            self.interaction_date = utc_date
        else:
            if not content or not content.strip():
                raise ValueError("Content notes require content")
            if interaction_date is not None:
                raise ValueError("Content notes cannot have interaction date")
            self.interaction_date = None

        self.contact_id = contact_id
        self.is_interaction = is_interaction
        self.content = content.strip() if content else None
        self.statements: List[Statement] = []
        self.tags: List["Tag"] = []

    def update_content(self, new_content: str) -> None:
        """Update the note's content.

        Args:
            new_content: New content for the note

        Raises:
            ValueError: If new_content is empty or note is interaction-only
        """
        if self.is_interaction:
            raise ValueError("Cannot update content of interaction-only note")
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
        from .tag_model import Tag, EntityType

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
