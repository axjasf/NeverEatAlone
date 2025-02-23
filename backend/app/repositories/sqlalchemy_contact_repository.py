"""SQLAlchemy implementation of contact repository."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, UTC
from sqlalchemy import select, and_, text
from sqlalchemy.orm import Session, selectinload

from ..models.domain.contact_model import Contact
from ..models.domain.tag_model import Tag, EntityType
from .interfaces import ContactRepository
from ..models.orm.contact_orm import ContactORM
from ..models.orm.tag_orm import TagORM


class SQLAlchemyContactRepository:
    """SQLAlchemy implementation of Contact repository.

    All datetime fields are handled in UTC timezone:
    - Input datetimes must be timezone-aware
    - Storage is always in UTC
    - Retrieved datetimes are always in UTC
    """

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy database session
        """
        self._session = session

    def save(self, contact: Contact) -> Contact:
        """Save a contact.

        Args:
            contact: The contact to save

        Returns:
            The saved contact with any updates from the database

        Note:
            All datetime fields are stored in UTC timezone.
        """
        # Convert domain model to ORM
        # last_contact is already in UTC from domain model
        contact_orm = ContactORM(
            id=contact.id,
            name=contact.name,
            first_name=contact.first_name,
            briefing_text=contact.briefing_text,
            sub_information=contact.sub_information,
            last_contact=contact.last_contact,  # Already in UTC
            contact_briefing_text=contact.contact_briefing_text,
        )

        # Merge to handle both insert and update
        contact_orm = self._session.merge(contact_orm)
        self._session.flush()

        # Save tags (last_contact is already in UTC)
        for tag in contact.tags:
            tag_orm = TagORM(
                entity_id=contact.id,
                entity_type=EntityType.CONTACT,
                name=tag.name,
                frequency_days=tag.frequency_days,
                last_contact=tag.last_contact,  # Already in UTC
            )
            self._session.merge(tag_orm)

        self._session.flush()
        return contact

    def find_by_id(self, contact_id: UUID) -> Optional[Contact]:
        """Find a contact by ID.

        Args:
            contact_id: UUID of the contact to find

        Returns:
            Contact if found, None otherwise

        Note:
            Retrieved datetime fields are in UTC timezone.
        """
        stmt = (
            select(ContactORM)
            .options(selectinload(ContactORM.tags))
            .where(ContactORM.id == contact_id)
        )
        contact_orm = self._session.execute(stmt).unique().scalar_one_or_none()

        if contact_orm is None:
            return None

        # Convert to domain model
        # last_contact from DB is already in UTC
        contact = Contact(
            name=contact_orm.name,
            first_name=contact_orm.first_name,
            briefing_text=contact_orm.briefing_text,
            sub_information=contact_orm.sub_information,
            last_contact=contact_orm.last_contact,  # Already in UTC
        )
        contact.id = contact_orm.id
        contact.contact_briefing_text = contact_orm.contact_briefing_text

        # Add tags (last_contact from DB is already in UTC)
        for tag_orm in contact_orm.tags:
            tag = Tag(
                entity_id=tag_orm.entity_id,
                entity_type=EntityType.CONTACT,
                name=tag_orm.name,
            )
            if tag_orm.frequency_days is not None:
                tag.set_frequency(tag_orm.frequency_days)
                if tag_orm.last_contact is not None:
                    tag.update_last_contact(tag_orm.last_contact)  # Already in UTC
            contact.tags.append(tag)

        return contact

    def find_by_tag(self, tag_name: str) -> List[Contact]:
        """Find contacts by tag name.

        Args:
            tag_name: Name of the tag to search for

        Returns:
            List of contacts with the specified tag
        """
        # Find all contact IDs with the given tag
        tag_stmt = select(TagORM.entity_id).where(
            and_(
                TagORM.name == tag_name,
                TagORM.entity_type == EntityType.CONTACT,
            )
        )
        contact_ids = self._session.execute(tag_stmt).scalars().all()

        # Load each contact
        contacts = []
        for contact_id in contact_ids:
            contact = self.find_by_id(contact_id)
            if contact is not None:
                contacts.append(contact)

        return contacts

    def find_stale(self) -> List[Contact]:
        """Find contacts with stale tags.

        Returns:
            List of contacts that have at least one stale tag

        Note:
            All datetime comparisons are done in UTC timezone.
        """
        now = datetime.now(UTC)

        # Find all contact IDs with stale tags using SQLite's datetime functions
        tag_stmt = (
            select(TagORM.entity_id)
            .where(
                and_(
                    TagORM.entity_type == EntityType.CONTACT,
                    TagORM.frequency_days.is_not(None),
                    TagORM.last_contact.is_not(None),
                    # Use SQLite's julianday function to calculate date differences
                    text("julianday(:now) - julianday(last_contact) > frequency_days"),
                )
            )
            .params(now=now.isoformat())  # UTC ISO format
        )

        # Execute the query
        contact_ids = self._session.execute(tag_stmt).scalars().all()

        # Load each contact
        contacts = []
        for contact_id in contact_ids:
            contact = self.find_by_id(contact_id)
            if contact is not None:
                contacts.append(contact)

        return contacts

    def delete(self, contact: Contact) -> None:
        """Delete a contact.

        Args:
            contact: The contact to delete
        """
        # Delete associated tags first
        self._session.query(TagORM).filter(
            and_(
                TagORM.entity_id == contact.id,
                TagORM.entity_type == EntityType.CONTACT,
            )
        ).delete()

        # Delete the contact
        self._session.query(ContactORM).filter(ContactORM.id == contact.id).delete()
        self._session.flush()

    def find_all(self) -> List[Contact]:
        """Find all contacts.

        Returns:
            List of all contacts
        """
        stmt = select(ContactORM).options(selectinload(ContactORM.tags))
        contact_orms = self._session.execute(stmt).unique().scalars().all()

        contacts = []
        for contact_orm in contact_orms:
            contact = Contact(
                name=contact_orm.name,
                first_name=contact_orm.first_name,
                briefing_text=contact_orm.briefing_text,
                sub_information=contact_orm.sub_information,
            )
            contact.id = contact_orm.id
            contact.last_contact = contact_orm.last_contact
            contact.contact_briefing_text = contact_orm.contact_briefing_text

            # Add tags
            for tag_orm in contact_orm.tags:
                tag = Tag(
                    entity_id=tag_orm.entity_id,
                    entity_type=EntityType.CONTACT,
                    name=tag_orm.name,
                )
                if tag_orm.frequency_days is not None:
                    tag.set_frequency(tag_orm.frequency_days)
                    if tag_orm.last_contact is not None:
                        tag.update_last_contact(tag_orm.last_contact)
                contact.tags.append(tag)

            contacts.append(contact)

        return contacts

    def find_by_last_contact_before(self, date: datetime) -> List[Contact]:
        """Find contacts with last contact before a given date.

        Args:
            date: The date to compare against (must be timezone-aware)

        Returns:
            List of contacts with last contact before the given date

        Raises:
            ValueError: If date is not timezone-aware
        """
        # Ensure input date is timezone-aware
        if date.tzinfo is None:
            raise ValueError("Input date must be timezone-aware")

        # Convert to UTC for comparison
        utc_date = date.astimezone(UTC)

        stmt = (
            select(ContactORM)
            .options(selectinload(ContactORM.tags))
            .where(ContactORM.last_contact < utc_date)
        )
        contact_orms = self._session.execute(stmt).unique().scalars().all()

        contacts = []
        for contact_orm in contact_orms:
            # Convert to domain model (last_contact from DB is already in UTC)
            contact = Contact(
                name=contact_orm.name,
                first_name=contact_orm.first_name,
                briefing_text=contact_orm.briefing_text,
                sub_information=contact_orm.sub_information,
                last_contact=contact_orm.last_contact,  # Already in UTC
            )
            contact.id = contact_orm.id
            contact.contact_briefing_text = contact_orm.contact_briefing_text

            # Add tags (last_contact from DB is already in UTC)
            for tag_orm in contact_orm.tags:
                tag = Tag(
                    entity_id=tag_orm.entity_id,
                    entity_type=EntityType.CONTACT,
                    name=tag_orm.name,
                )
                if tag_orm.frequency_days is not None:
                    tag.set_frequency(tag_orm.frequency_days)
                    if tag_orm.last_contact is not None:
                        tag.update_last_contact(tag_orm.last_contact)  # Already in UTC
                contact.tags.append(tag)

            contacts.append(contact)

        return contacts
