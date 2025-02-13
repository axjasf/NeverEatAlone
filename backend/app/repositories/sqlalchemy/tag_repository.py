"""SQLAlchemy implementation of TagRepository."""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy import String, select, and_, UniqueConstraint
from sqlalchemy.orm import Session, Mapped, mapped_column
from ...models.tag import Tag, EntityType
from ...database import Base
from ...models.base import GUID


class TagORM(Base):
    """ORM model for storing tags in the database.

    This class handles the persistence details, keeping them separate
    from the domain model (Tag). The ID is managed here, not in the
    domain model.

    A tag is uniquely identified in the domain by:
    - entity_id
    - entity_type
    - name

    But for database efficiency, we also maintain an internal ID.
    """
    __tablename__ = "tag_orm"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid4)
    entity_id: Mapped[UUID] = mapped_column(GUID, nullable=False)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    frequency_days: Mapped[Optional[int]] = mapped_column(nullable=True)
    last_contact: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Add a unique constraint on the natural key
    __table_args__ = (
        UniqueConstraint('entity_id', 'entity_type', 'name', name='uq_tag_natural_key'),
    )

    @classmethod
    def from_domain(cls, tag: Tag) -> "TagORM":
        """Create an ORM instance from a domain model instance."""
        return cls(
            entity_id=tag.entity_id,
            entity_type=tag.entity_type,
            name=tag.name,
            frequency_days=tag.frequency_days,
            last_contact=tag.last_contact
        )

    def to_domain(self) -> Tag:
        """Convert this ORM instance to a domain model instance."""
        tag = Tag(
            entity_id=self.entity_id,
            entity_type=EntityType(self.entity_type),
            name=self.name
        )
        tag.frequency_days = self.frequency_days
        # Ensure timezone-aware datetime
        if self.last_contact is not None:
            if self.last_contact.tzinfo is None:
                tag.last_contact = self.last_contact.replace(tzinfo=timezone.utc)
            else:
                tag.last_contact = self.last_contact
        else:
            tag.last_contact = None
        return tag


class SQLAlchemyTagRepository:
    """SQLAlchemy implementation of TagRepository."""

    def __init__(self, session: Session):
        """Initialize the repository.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def save(self, tag: Tag) -> Tag:
        """Save a tag to the database.

        Args:
            tag: The tag to save

        Returns:
            The managed Tag instance
        """
        # Look for existing tag with same natural key
        stmt = select(TagORM).where(and_(
            TagORM.entity_id == tag.entity_id,
            TagORM.entity_type == tag.entity_type,
            TagORM.name == tag.name
        ))
        existing = self.session.execute(stmt).scalar_one_or_none()

        if existing:
            # Update existing tag
            existing.frequency_days = tag.frequency_days
            existing.last_contact = tag.last_contact
            self.session.flush()
            return existing.to_domain()
        else:
            # Create new tag
            orm_tag = TagORM.from_domain(tag)
            self.session.add(orm_tag)
            self.session.flush()
            return orm_tag.to_domain()

    def find_by_id(self, id: UUID) -> Optional[Tag]:
        """Find a tag by its internal ID.

        Note: This method is primarily for internal use. Domain code should
        use find_by_entity or find_by_name instead.
        """
        orm_tag = self.session.get(TagORM, id)
        return orm_tag.to_domain() if orm_tag else None

    def find_by_name(self, name: str) -> List[Tag]:
        """Find all tags with a given name (case-insensitive)."""
        stmt = select(TagORM).where(TagORM.name == name.lower())
        return [t.to_domain() for t in self.session.execute(stmt).scalars()]

    def find_by_entity(self, entity_id: UUID, entity_type: EntityType) -> List[Tag]:
        """Find all tags for a given entity."""
        # Clear session cache and ensure pending changes are flushed
        self.session.expire_all()
        self.session.flush()

        # Use fresh query
        stmt = select(TagORM).where(and_(
            TagORM.entity_id == entity_id,
            TagORM.entity_type == entity_type.value
        ))

        # Execute query and refresh session
        result = self.session.execute(stmt).scalars().all()
        self.session.expire_all()
        return [t.to_domain() for t in result]

    def find_stale(self) -> List[Tag]:
        """Find all tags that are stale based on their frequency and last contact.

        A tag is considered stale if:
        1. It has a frequency set (frequency_days is not null)
        2. It has a last_contact date set
        3. The current date minus the frequency_days is greater than the last_contact date
        """
        # Get all tags with frequency and last_contact set
        stmt = select(TagORM).where(and_(
            TagORM.frequency_days.is_not(None),
            TagORM.last_contact.is_not(None)
        ))
        tags = [t.to_domain() for t in self.session.execute(stmt).scalars()]

        # Filter stale tags in Python to use the domain model's time handling
        return [tag for tag in tags if tag.is_stale()]

    def delete(self, tag: Tag) -> None:
        """Delete a tag from the database.

        Args:
            tag: The tag to delete
        """
        # Clear session cache
        self.session.expire_all()

        # Find the managed instance
        stmt = select(TagORM).where(and_(
            TagORM.entity_id == tag.entity_id,
            TagORM.entity_type == tag.entity_type,
            TagORM.name == tag.name
        ))
        managed_tag = self.session.execute(stmt).scalar_one_or_none()

        if managed_tag:
            # Delete using ORM
            self.session.delete(managed_tag)
            # Ensure changes are synchronized
            self.session.flush()
            self.session.expire_all()
