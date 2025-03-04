"""Test suite for ContactService implementation.

This module contains comprehensive tests for the ContactService class, covering all
core operations and their requirements as specified in CR-48.

Test Categories:
1. Basic Operations (FR1.1.*, FR1.3.*)
2. Tag Operations (FR2.1.*)
3. Interaction Operations (FR1.1.4-5, FR2.2.*)
4. Search Operations (FR1.3.3)
5. Error Handling
6. Transaction Boundaries
7. Repository Dependencies
"""

import pytest
from datetime import datetime, timezone
from typing import Dict, List, Any, Callable
from uuid import UUID
from unittest.mock import Mock, create_autospec
from sqlalchemy.orm import Session, sessionmaker

from app.services.contact_service import ContactService
from app.models.domain.contact_model import Contact
from app.models.domain.note_model import Note
from app.models.domain.tag_model import Tag, EntityType
from app.models.domain.template_model import Template, CategoryDefinition, FieldDefinition
from app.services.base_service import ServiceError, ValidationError, NotFoundError
from app.repositories.interfaces import ContactRepository, TemplateRepository
from app.models.orm.template_orm import TemplateVersionORM

# Test Fixtures
@pytest.fixture
def contact_service(session_factory: Callable[[], Session]) -> ContactService:
    """Create a ContactService instance with test session factory."""
    return ContactService(session_factory)

@pytest.fixture
def sample_contact_data() -> Dict[str, Any]:
    """Sample contact data for testing."""
    return {
        "name": "Test Contact",
        "briefing_text": "Test contact for unit tests"
    }

@pytest.fixture
def sample_tags() -> List[str]:
    """Create sample tags for testing."""
    return ["#test", "#unittest", "#contact"]

@pytest.fixture
def default_template(session_factory: Callable[[], Session], sample_template_data: Dict[str, Any]) -> Template:
    """Create a default template in the database."""
    with session_factory() as session:
        template = Template(**sample_template_data)
        # Convert CategoryDefinition objects to dictionaries
        categories_dict = {
            name: {
                'name': cat.name,
                'description': cat.description,
                'fields': {
                    field_name: {
                        'name': field.name,
                        'type': field.type,
                        'description': field.description,
                        'display_format': field.display_format,
                        'reminder_template': field.reminder_template,
                        'validators': field.validators
                    }
                    for field_name, field in cat.fields.items()
                }
            }
            for name, cat in template.categories.items()
        }

        template_orm = TemplateVersionORM(
            id=template.id,
            version=template.version,
            categories=categories_dict,
            created_at=template.created_at,
            updated_at=template.updated_at
        )
        session.add(template_orm)
        session.commit()
        return template

# Basic Operations Tests [FR1.1.*, FR1.3.*]
class TestBasicOperations:
    """Test basic CRUD operations for contacts."""

    def test_create_contact_with_valid_data(self, contact_service: ContactService, sample_contact_data: Dict[str, Any]):
        """Test creating contact with valid data [FR1.1.1, FR1.1.2]."""
        # When: Creating a contact with valid data
        contact = contact_service.create_with_tags(sample_contact_data, [])

        # Then: Contact should be created with correct data
        assert contact.name == sample_contact_data["name"]
        assert contact.briefing_text == sample_contact_data["briefing_text"]
        assert contact.tags == []

    def test_create_contact_with_tags(self, contact_service: ContactService, sample_contact_data: Dict[str, Any], sample_tags: List[str]):
        """Test creating contact with tags [FR1.1.1, FR1.1.2, FR2.1.1, FR2.1.4].

        This test verifies that:
        1. Contact can be created with initial tags
        2. Tags are properly normalized and stored
        3. No duplicate tags are created
        4. Tags are associated with the contact correctly
        """
        # Given: Sample contact data and tags with some duplicates and variations
        tags_with_duplicates = sample_tags + ["#Test", "#unittest", "#newTag"]  # Mixed case and duplicate

        # When: Creating a contact with tags
        contact = contact_service.create_with_tags(sample_contact_data, tags_with_duplicates)

        # Then: Contact should be created with correct data and normalized tags
        assert contact.name == sample_contact_data["name"]
        assert contact.briefing_text == sample_contact_data["briefing_text"]

        # Verify tags are normalized and deduplicated
        expected_tags = {"#test", "#unittest", "#contact", "#newtag"}  # All lowercase, no duplicates
        actual_tags = {tag.name for tag in contact.tags}
        assert actual_tags == expected_tags

        # Verify each tag is properly initialized
        for tag in contact.tags:
            assert tag.created_at is not None
            assert tag.entity_type == EntityType.CONTACT.value
            assert tag.entity_id == contact.id
            assert tag.frequency_days is None  # No frequency set by default

    def test_update_contact_details(self, contact_service: ContactService, sample_contact_data: Dict[str, Any]):
        """Test updating contact details [FR1.1.3].

        This test verifies that:
        1. Contact details can be updated
        2. Only specified fields are updated
        3. Updates are persisted correctly
        4. Non-existent contacts are handled properly
        """
        # Given: An existing contact
        contact = contact_service.create_with_tags(sample_contact_data, [])

        # When: Updating contact details
        update_data = {
            "name": "Updated Name",
            "briefing_text": "Updated briefing text"
        }
        updated_contact = contact_service.update(contact.id, update_data)

        # Then: Contact should be updated with new data
        assert updated_contact.name == update_data["name"]
        assert updated_contact.briefing_text == update_data["briefing_text"]

        # And: Updates should persist
        retrieved_contact = contact_service.get_by_id(contact.id)
        assert retrieved_contact.name == update_data["name"]
        assert retrieved_contact.briefing_text == update_data["briefing_text"]

        # When: Trying to update a non-existent contact
        non_existent_id = UUID("00000000-0000-0000-0000-000000000000")
        with pytest.raises(NotFoundError) as exc_info:
            contact_service.update(non_existent_id, update_data)
        assert str(exc_info.value).endswith(f"Contact {non_existent_id} not found")

    def test_delete_contact_with_cleanup(self, contact_service: ContactService, sample_contact_data: Dict[str, Any]):
        """Test contact deletion with proper cleanup [FR1.3.2]."""
        pass

    def test_get_contact_by_id(self, contact_service: ContactService, sample_contact_data: Dict[str, Any]):
        """Test retrieving contact by ID [FR1.3.1]."""
        pass

# Tag Operations Tests [FR2.1.*]
class TestTagOperations:
    """Test tag-related operations."""

    def test_add_tags_to_contact(self, contact_service: ContactService, sample_contact_data: Dict[str, Any], sample_tags: List[str]):
        """Test adding tags to contact [FR2.1.1, FR2.1.4]."""
        pass

    def test_remove_tags_from_contact(self, contact_service: ContactService, sample_contact_data: Dict[str, Any], sample_tags: List[str]):
        """Test removing tags from contact [FR2.1.3]."""
        pass

    def test_tag_normalization(self, contact_service: ContactService, sample_contact_data: Dict[str, Any]):
        """Test tag normalization rules [FR2.1.2]."""
        pass

    def test_prevent_duplicate_tags(self, contact_service: ContactService, sample_contact_data: Dict[str, Any]):
        """Test prevention of duplicate tags [FR2.1.3]."""
        pass

# Interaction Operations Tests [FR1.1.4-5, FR2.2.*]
class TestInteractionOperations:
    """Test interaction tracking and frequency operations."""

    def test_record_interaction(self, contact_service: ContactService, sample_contact_data: Dict[str, Any]):
        """Test recording interaction with note [FR1.1.4]."""
        pass

    def test_update_last_contact_timestamp(self, contact_service: ContactService, sample_contact_data: Dict[str, Any]):
        """Test updating last contact timestamp [FR1.1.5]."""
        pass

    def test_update_tag_frequency(self, contact_service: ContactService, sample_contact_data: Dict[str, Any], sample_tags: List[str]):
        """Test updating tag frequency settings [FR2.2.1, FR2.2.4]."""
        pass

    def test_track_tag_interactions(self, contact_service: ContactService, sample_contact_data: Dict[str, Any], sample_tags: List[str]):
        """Test tracking per-tag interactions [FR2.2.5, FR2.2.6]."""
        pass

# Search Operations Tests [FR1.3.3]
class TestSearchOperations:
    """Test contact search operations."""

    def test_search_by_name(self, contact_service: ContactService, sample_contact_data: Dict[str, Any]):
        """Test searching contacts by name."""
        pass

    def test_search_by_tags(self, contact_service: ContactService, sample_contact_data: Dict[str, Any], sample_tags: List[str]):
        """Test searching contacts by tags."""
        pass

    def test_search_by_date_range(self, contact_service: ContactService, sample_contact_data: Dict[str, Any]):
        """Test searching contacts by interaction date range."""
        pass

    def test_search_by_staleness(self, contact_service: ContactService, sample_contact_data: Dict[str, Any], sample_tags: List[str]):
        """Test searching contacts by tag staleness."""
        pass

    def test_search_pagination(self, contact_service: ContactService, sample_contact_data: Dict[str, Any]):
        """Test search result pagination."""
        pass

# Error Handling Tests
class TestErrorHandling:
    """Test error handling scenarios."""

    def test_not_found_handling(self, contact_service: ContactService):
        """Test handling of non-existent contact operations."""
        pass

    def test_validation_error_handling(self, contact_service: ContactService):
        """Test handling of invalid input data."""
        pass

    def test_transaction_error_handling(self, contact_service: ContactService):
        """Test handling of transaction failures."""
        pass

# Transaction Boundary Tests
class TestTransactionBoundaries:
    """Test transaction boundaries and rollback scenarios."""

    def test_create_rollback_on_error(self, contact_service: ContactService, sample_contact_data: Dict[str, Any]):
        """Test transaction rollback on create failure."""
        pass

    def test_update_rollback_on_error(self, contact_service: ContactService, sample_contact_data: Dict[str, Any]):
        """Test transaction rollback on update failure."""
        pass

    def test_delete_rollback_on_error(self, contact_service: ContactService, sample_contact_data: Dict[str, Any]):
        """Test transaction rollback on delete failure."""
        pass

# Repository Dependency Tests
class TestRepositoryDependencies:
    """Test repository dependency injection and usage."""

    @pytest.fixture
    def mock_contact_repo(self) -> Mock:
        """Create a mock contact repository."""
        return create_autospec(ContactRepository, instance=True)

    @pytest.fixture
    def mock_template_repo(self) -> Mock:
        """Create a mock template repository."""
        return create_autospec(TemplateRepository, instance=True)

    @pytest.fixture
    def sample_template_data(self) -> Dict[str, Any]:
        """Create sample template data for testing."""
        now = datetime.now(timezone.utc)
        personal_category = CategoryDefinition(
            name="personal",
            description="Personal information",
            fields={
                "email": FieldDefinition(
                    name="email",
                    type="email",
                    description="Email address"
                )
            }
        )
        work_category = CategoryDefinition(
            name="work",
            description="Work information",
            fields={
                "company": FieldDefinition(
                    name="company",
                    type="string",
                    description="Company name"
                )
            }
        )
        return {
            "id": UUID("12345678-1234-5678-1234-567812345678"),
            "categories": {
                "personal": personal_category,
                "work": work_category
            },
            "version": 1,
            "created_at": now,
            "updated_at": now
        }

    def test_service_accepts_repository_dependencies(
        self,
        session_factory: Callable[[], Session],
        mock_contact_repo: Mock,
        mock_template_repo: Mock
    ):
        """Test that service accepts repository dependencies in constructor."""
        # When: Creating service with repository dependencies
        service = ContactService(
            session_factory,
            contact_repository=mock_contact_repo,
            template_repository=mock_template_repo
        )

        # Then: Repositories should be properly set
        assert service._contact_repository == mock_contact_repo
        assert service._template_repository == mock_template_repo

    def test_service_works_without_repository_dependencies(
        self,
        session_factory: Callable[[], Session],
        default_template: Template
    ):
        """Test that service works without explicit repository dependencies."""
        # When: Creating service without repository dependencies
        service = ContactService(session_factory)

        # Then: Default repositories should be None initially
        assert service._contact_repository is None
        assert service._template_repository is None

        # And: Should create repositories on demand in methods
        template = service.get_current_template()
        assert isinstance(template, Template)
        assert template.version == default_template.version
        assert template.categories == default_template.categories

    def test_get_current_template_uses_injected_repository(
        self,
        session_factory: Callable[[], Session],
        mock_template_repo: Mock,
        sample_template_data: Dict[str, Any]
    ):
        """Test that get_current_template uses injected repository."""
        # Given: A service with injected template repository
        template = Template(**sample_template_data)
        mock_template_repo.get_latest_template.return_value = template
        service = ContactService(session_factory, template_repository=mock_template_repo)

        # When: Getting current template
        result = service.get_current_template()

        # Then: Should use injected repository
        assert result == template
        mock_template_repo.get_latest_template.assert_called_once()

    def test_get_by_id_uses_injected_repository(
        self,
        session_factory: Callable[[], Session],
        mock_contact_repo: Mock,
        sample_contact_data: Dict[str, Any]
    ):
        """Test that get_by_id uses injected repository."""
        # Given: A service with injected contact repository
        contact = Contact(
            name=sample_contact_data["name"],
            briefing_text=sample_contact_data["briefing_text"]
        )
        mock_contact_repo.find_by_id.return_value = contact
        service = ContactService(session_factory, contact_repository=mock_contact_repo)

        # When: Getting contact by ID
        result = service.get_by_id(contact.id)

        # Then: Should use injected repository
        assert result == contact
        mock_contact_repo.find_by_id.assert_called_once_with(contact.id)
