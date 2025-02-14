"""Tag repository interface."""
from typing import Protocol, Optional, List
from uuid import UUID
from ..domain.tag import Tag, EntityType


class TagRepository(Protocol):
    """Interface for tag persistence operations."""

    def save(self, tag: Tag) -> None:
        """Save a tag.

        Args:
            tag: The tag to save
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

    def find_by_entity(
        self,
        entity_id: UUID,
        entity_type: EntityType
    ) -> List[Tag]:
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
