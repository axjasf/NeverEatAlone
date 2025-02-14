"""SQLAlchemy implementation of the tag repository."""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..domain.tag import Tag, EntityType
from .interfaces import TagRepository
from ..orm.tag import TagORM
from datetime import timezone


class SQLAlchemyTagRepository(TagRepository):
    """SQLAlchemy implementation of tag persistence."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository.

        Args:
            session: SQLAlchemy session
        """
        self.session = session

    def save(self, tag: Tag) -> Tag:
        """Save a tag.

        Args:
            tag: The tag to save

        Returns:
            The saved tag with any updates from the database
        """
        # Check if tag already exists by natural key
        stmt = select(TagORM).where(
            TagORM.entity_id == tag.entity_id,
            TagORM.entity_type == tag.entity_type,
            TagORM.name == tag.name
        )
        existing = self.session.execute(stmt).scalar_one_or_none()

        if existing:
            # Update existing tag
            existing.frequency_days = tag.frequency_days
            existing.last_contact = tag.last_contact
            tag.id = existing.id  # Update domain model with DB ID
        else:
            # Create new tag
            tag_orm = TagORM(
                id=tag.id,
                entity_id=tag.entity_id,
                entity_type=tag.entity_type,
                name=tag.name,
                frequency_days=tag.frequency_days,
                last_contact=tag.last_contact
            )
            self.session.add(tag_orm)

        self.session.commit()
        return tag

    def find_by_id(self, tag_id: UUID) -> Optional[Tag]:
        """Find a tag by its ID.

        Args:
            tag_id: The ID to search for

        Returns:
            The tag if found, None otherwise
        """
        tag_orm = self.session.get(TagORM, tag_id)
        if not tag_orm:
            return None
        return self._to_domain(tag_orm)

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
        stmt = select(TagORM).where(
            TagORM.entity_id == entity_id,
            TagORM.entity_type == entity_type.value
        )
        tags_orm = self.session.execute(stmt).scalars().all()
        return [self._to_domain(tag) for tag in tags_orm]

    def find_by_name(self, name: str) -> List[Tag]:
        """Find all tags with a specific name.

        Args:
            name: The tag name to search for

        Returns:
            List of tags with the name
        """
        stmt = select(TagORM).where(TagORM.name == name.lower())
        tags_orm = self.session.execute(stmt).scalars().all()
        return [self._to_domain(tag) for tag in tags_orm]

    def find_stale(self) -> List[Tag]:
        """Find all tags that are stale based on their frequency.

        Returns:
            List of stale tags
        """
        # Convert to domain models first to use domain logic for staleness
        stmt = select(TagORM).where(TagORM.frequency_days.is_not(None))
        tags_orm = self.session.execute(stmt).scalars().all()
        tags = [self._to_domain(tag) for tag in tags_orm]
        return [tag for tag in tags if tag.is_stale()]

    def delete(self, tag: Tag) -> None:
        """Delete a tag.

        Args:
            tag: The tag to delete
        """
        tag_orm = self.session.get(TagORM, tag.id)
        if tag_orm:
            self.session.delete(tag_orm)
            self.session.commit()

    def _to_domain(self, tag_orm: TagORM) -> Tag:
        """Convert ORM model to domain model.

        Args:
            tag_orm: The ORM model to convert

        Returns:
            The domain model
        """
        tag = Tag(
            entity_id=tag_orm.entity_id,
            entity_type=EntityType(tag_orm.entity_type),
            name=tag_orm.name
        )
        tag.frequency_days = tag_orm.frequency_days
        # Ensure timezone is preserved
        if tag_orm.last_contact and tag_orm.last_contact.tzinfo is None:
            tag.last_contact = tag_orm.last_contact.replace(tzinfo=timezone.utc)
        else:
            tag.last_contact = tag_orm.last_contact
        return tag
