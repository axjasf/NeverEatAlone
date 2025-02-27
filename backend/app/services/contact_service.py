"""Contact Service Implementation.

This module implements the ContactService class, providing business operations
for managing contacts and their associated data (tags, notes, interactions)
in a consistent and transactional way.

See SERVICE_CONTACT.md for detailed design documentation.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from ..models.domain.contact_model import Contact
from ..models.domain.template_model import Template
from ..models.orm.template_orm import TemplateVersionORM
from .base_service import BaseService, ServiceError, ValidationError, NotFoundError

class ContactService(BaseService):
    """Contact Service implementation following BaseService patterns."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        """Initialize the contact service.

        Args:
            session_factory: Factory function that creates database sessions
        """
        super().__init__(session_factory)

    def get_current_template(self) -> Template:
        """Get the current active template.

        Returns:
            Template: The current active template

        Raises:
            ServiceError: If no active template exists
        """
        with self.in_transaction() as session:
            try:
                stmt = select(TemplateVersionORM).order_by(desc(TemplateVersionORM.version))
                template = session.execute(stmt).scalars().first()
                if not template:
                    raise ServiceError("get_current_template", ValueError("No active template found"))
                return Template.model_validate(template)
            except Exception as e:
                if not isinstance(e, ServiceError):
                    raise ServiceError("get_current_template", e)
                raise

    def create_with_tags(
        self,
        contact_data: Dict[str, Any],
        tags: List[str]
    ) -> Contact:
        """Create a new contact with associated tags.

        Requirements: [FR1.1.1, FR1.1.2, FR2.1.1, FR2.1.4]

        Args:
            contact_data: Dictionary containing contact information
            tags: List of tags to associate with the contact

        Returns:
            Created Contact instance

        Raises:
            ValidationError: If contact_data is invalid
            ServiceError: If creation fails
        """
        self.logger.info("Creating contact with tags", extra={"contact_data": contact_data, "tags": tags})
        with self.in_transaction() as session:
            try:
                contact = Contact(**contact_data)
                session.add(contact)
                contact.set_hashtags(tags)
                return contact
            except Exception as e:
                raise ServiceError("create_with_tags", e)

    def update(
        self,
        contact_id: UUID,
        data: Dict[str, Any]
    ) -> Contact:
        """Update contact details.

        Requirements: [FR1.1.3]

        Args:
            contact_id: UUID of the contact to update
            data: Dictionary containing fields to update

        Returns:
            Updated Contact instance

        Raises:
            ValidationError: If data is invalid
            NotFoundError: If contact doesn't exist
            ServiceError: If update fails
        """
        self.logger.info("Updating contact", extra={"contact_id": contact_id, "data": data})
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError("update", ValueError(f"Contact {contact_id} not found"))
                for key, value in data.items():
                    setattr(contact, key, value)
                return contact
            except Exception as e:
                if not isinstance(e, ServiceError):
                    raise ServiceError("update", e)
                raise

    def delete(self, contact_id: UUID) -> None:
        """Delete a contact and associated data.

        Requirements: [FR1.3.2]
        - Must remove all contact information
        - Must remove all tag associations
        - Must remove all interaction records
        - Must remove all notes
        - Must preserve tag definitions if used by other contacts
        - Must handle non-existent contacts gracefully

        Args:
            contact_id: UUID of the contact to delete

        Raises:
            NotFoundError: If contact doesn't exist
            ServiceError: If deletion fails
        """
        self.logger.info("Deleting contact", extra={"contact_id": contact_id})
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError("delete", ValueError(f"Contact {contact_id} not found"))

                # Clean up notes (which includes interactions)
                for note in contact.notes[:]:  # Copy list to avoid modification during iteration
                    contact.remove_note(note)
                    session.delete(note)

                # Remove tag associations but preserve tags
                contact.tags.clear()
                session.delete(contact)
            except Exception as e:
                if not isinstance(e, ServiceError):
                    raise ServiceError("delete", e)
                raise

    def get_by_id(self, contact_id: UUID) -> Contact:
        """Get a contact by ID.

        Requirements: [FR1.3.1]

        Args:
            contact_id: UUID of the contact to retrieve

        Returns:
            Contact instance

        Raises:
            ValidationError: If contact_id is invalid
            NotFoundError: If contact doesn't exist
        """
        self.logger.info("Getting contact by ID", extra={"contact_id": contact_id})
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError("get_by_id", ValueError(f"Contact {contact_id} not found"))
                return contact
            except Exception as e:
                if not isinstance(e, ServiceError):
                    raise ServiceError("get_by_id", e)
                raise

    def search(
        self,
        criteria: Dict[str, Any],
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> List[Contact]:
        """Search contacts by criteria.

        Requirements: [FR1.3.3]

        Args:
            criteria: Search criteria dictionary
            page: Optional page number for pagination
            page_size: Optional page size for pagination

        Returns:
            List of matching Contact instances

        Raises:
            ValidationError: If criteria or pagination params are invalid
        """
        self.logger.info("Searching contacts", extra={"criteria": criteria, "page": page, "page_size": page_size})
        with self.in_transaction() as session:
            try:
                # Validate criteria
                if not isinstance(criteria.get('name', ''), str):
                    raise ValidationError("search", ValueError("Name criteria must be a string"))
                if page is not None and page < 1:
                    raise ValidationError("search", ValueError("Page number must be positive"))

                # Build query
                query = session.query(Contact)
                # ... query building logic ...

                return query.all()
            except Exception as e:
                if not isinstance(e, ServiceError):
                    raise ServiceError("search", e)
                raise

    def add_tags(
        self,
        contact_id: UUID,
        tags: List[str]
    ) -> Contact:
        """Add tags to a contact.

        Requirements: [FR2.1.1, FR2.1.3, FR2.1.4]
        - Must normalize tags to lowercase
        - Must prevent duplicate tags
        - Must handle non-existent contacts gracefully

        Args:
            contact_id: UUID of the contact
            tags: List of tags to add

        Returns:
            Updated Contact instance

        Raises:
            ValidationError: If tags format is invalid
            NotFoundError: If contact doesn't exist
            ServiceError: If tag operation fails
        """
        self.logger.info("Adding tags to contact", extra={"contact_id": contact_id, "tags": tags})
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError("add_tags", ValueError(f"Contact {contact_id} not found"))

                # Add each tag individually
                for tag in tags:
                    contact.add_tag(tag)
                return contact
            except Exception as e:
                if not isinstance(e, ServiceError):
                    raise ServiceError("add_tags", e)
                raise

    def remove_tags(
        self,
        contact_id: UUID,
        tags: List[str]
    ) -> Contact:
        """Remove tags from a contact.

        Requirements: [FR2.1.3]

        Args:
            contact_id: UUID of the contact
            tags: List of tags to remove

        Returns:
            Updated Contact instance

        Raises:
            ValidationError: If tags format is invalid
            NotFoundError: If contact doesn't exist
            ServiceError: If tag removal fails
        """
        self.logger.info("Removing tags from contact", extra={"contact_id": contact_id, "tags": tags})
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError("remove_tags", ValueError(f"Contact {contact_id} not found"))

                # Remove matching tags
                for tag in contact.tags[:]:  # Copy list to avoid modification during iteration
                    if tag.name in tags:
                        contact.remove_tag(tag)
                return contact
            except Exception as e:
                if not isinstance(e, ServiceError):
                    raise ServiceError("remove_tags", e)
                raise

    def record_interaction(
        self,
        contact_id: UUID,
        date: datetime,
        note: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Contact:
        """Record an interaction with a contact.

        Requirements: [FR1.1.4, FR1.1.5, FR2.2.2, FR2.2.5, FR2.2.6]

        Args:
            contact_id: UUID of the contact
            date: Interaction date
            note: Optional note text
            tags: Optional list of tags for the interaction

        Returns:
            Updated Contact instance

        Raises:
            ValidationError: If date is invalid or in future
            NotFoundError: If contact doesn't exist
            ServiceError: If interaction recording fails
        """
        self.logger.info("Recording interaction", extra={
            "contact_id": contact_id,
            "date": date,
            "note": note,
            "tags": tags
        })
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError("record_interaction", ValueError(f"Contact {contact_id} not found"))

                # Record interaction using contact model
                interaction_note = contact.add_interaction(date, note)

                # Add any tags to the interaction
                if tags:
                    for tag in tags:
                        interaction_note.add_tag(tag)

                return contact
            except Exception as e:
                if not isinstance(e, ServiceError):
                    raise ServiceError("record_interaction", e)
                raise

    def update_tag_frequency(
        self,
        contact_id: UUID,
        tag_name: str,
        frequency_days: Optional[int]
    ) -> Contact:
        """Update contact-tag frequency settings.

        Requirements: [FR2.2.1, FR2.2.4]

        Args:
            contact_id: UUID of the contact
            tag_name: Tag to update frequency for
            frequency_days: Optional number of days for frequency, None to disable

        Returns:
            Updated Contact instance

        Raises:
            ValidationError: If frequency_days is negative
            NotFoundError: If contact or tag doesn't exist
            ServiceError: If frequency update fails
        """
        self.logger.info("Updating tag frequency", extra={
            "contact_id": contact_id,
            "tag_name": tag_name,
            "frequency_days": frequency_days
        })
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError("update_tag_frequency", ValueError(f"Contact {contact_id} not found"))

                # Validate frequency
                if frequency_days is not None and frequency_days < 0:
                    raise ValidationError("update_tag_frequency", ValueError("Frequency days cannot be negative"))

                # Find the tag and update its frequency
                tag = next((t for t in contact.tags if t.name == tag_name), None)
                if not tag:
                    raise NotFoundError("update_tag_frequency", ValueError(f"Tag {tag_name} not found on contact"))

                tag.frequency_days = frequency_days
                return contact
            except Exception as e:
                if not isinstance(e, ServiceError):
                    raise ServiceError("update_tag_frequency", e)
                raise

    def validate_sub_information(
        self,
        contact_id: UUID,
        sub_information: Dict[str, Any]
    ) -> bool:
        """Validate sub_information against current template.

        Requirements: [FR1.2.1, FR1.2.2]

        Args:
            contact_id: UUID of the contact
            sub_information: Dictionary of sub-information to validate

        Returns:
            bool indicating if validation passed

        Raises:
            ValidationError: If sub_information format is invalid
            NotFoundError: If contact doesn't exist
            ServiceError: If validation fails
        """
        self.logger.info("Validating sub-information", extra={
            "contact_id": contact_id,
            "sub_information": sub_information
        })
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError("validate_sub_information", ValueError(f"Contact {contact_id} not found"))

                # Get current template
                template = self.get_current_template()

                # Validate against template
                try:
                    template.validate_data(sub_information)
                    return True
                except ValueError as e:
                    raise ValidationError("validate_sub_information", e)
            except Exception as e:
                if not isinstance(e, ServiceError):
                    raise ServiceError("validate_sub_information", e)
                raise
