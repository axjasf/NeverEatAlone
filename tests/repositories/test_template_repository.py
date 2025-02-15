"""Tests for the Template repository."""

from datetime import datetime, UTC
from uuid import uuid4
from sqlalchemy.orm import Session
from backend.app.models.domain.template import (
    Template,
    CategoryDefinition,
    FieldDefinition,
)
from backend.app.repositories.sqlalchemy_template_repository import (
    SQLAlchemyTemplateRepository,
)


def create_test_template() -> Template:
    """Create a template for testing."""
    now = datetime.now(UTC)
    return Template(
        id=uuid4(),
        categories={
            "contact_info": CategoryDefinition(
                name="contact_info",
                description="Basic contact information",
                fields={
                    "phone": FieldDefinition(
                        name="phone", type="phone", description="Phone number"
                    )
                },
            )
        },
        version=1,
        created_at=now,
        updated_at=now,
    )


def test_template_save_and_get(db_session: Session) -> None:
    """Test saving and retrieving a template."""
    repository = SQLAlchemyTemplateRepository(db_session)
    template = create_test_template()

    # Save the template
    repository.save(template)

    # Get the template back
    retrieved = repository.get_by_id(template.id)
    assert retrieved is not None, "Template should be found after saving"

    # Verify all fields match
    assert retrieved.id == template.id
    assert retrieved.version == template.version
    assert retrieved.categories == template.categories
    assert retrieved.created_at == template.created_at
    assert (
        retrieved.updated_at == template.created_at
    )  # For versions, updated_at is same as created_at


def test_template_get_version(db_session: Session) -> None:
    """Test getting a specific version of a template."""
    repository = SQLAlchemyTemplateRepository(db_session)
    template = create_test_template()
    repository.save(template)

    # Create a new version
    new_template = template.evolve(
        new_fields={
            "contact_info": {
                "email": FieldDefinition(
                    name="email", type="email", description="Email address"
                )
            }
        }
    )
    repository.save(new_template)

    # Get original version
    original = repository.get_version(template.id, 1)
    assert original is not None, "Original version should be found"
    assert original.version == 1
    assert "email" not in original.categories["contact_info"].fields

    # Get new version
    evolved = repository.get_version(template.id, 2)
    assert evolved is not None, "New version should be found"
    assert evolved.version == 2
    assert "email" in evolved.categories["contact_info"].fields


def test_template_get_versions(db_session: Session) -> None:
    """Test getting all versions of a template."""
    repository = SQLAlchemyTemplateRepository(db_session)
    template = create_test_template()
    repository.save(template)

    # Create two new versions
    v2 = template.evolve(
        new_fields={
            "contact_info": {
                "email": FieldDefinition(
                    name="email", type="email", description="Email address"
                )
            }
        }
    )
    repository.save(v2)

    v3 = v2.evolve(
        new_fields={
            "contact_info": {
                "birthday": FieldDefinition(
                    name="birthday", type="date", description="Date of birth"
                )
            }
        }
    )
    repository.save(v3)

    # Get all versions
    versions = repository.get_versions(template.id)
    assert len(versions) == 3, "Should have three versions"

    # Verify we have all versions in order
    assert [v.version for v in versions] == [1, 2, 3]

    # Verify the content of each version
    assert "email" not in versions[0].categories["contact_info"].fields
    assert "email" in versions[1].categories["contact_info"].fields
    assert "birthday" not in versions[1].categories["contact_info"].fields
    assert "birthday" in versions[2].categories["contact_info"].fields


def test_template_get_nonexistent(db_session: Session) -> None:
    """Test getting a template that doesn't exist."""
    repository = SQLAlchemyTemplateRepository(db_session)
    result = repository.get_by_id(uuid4())
    assert result is None, "Should return None for nonexistent template"


def test_template_get_nonexistent_version(db_session: Session) -> None:
    """Test getting a version that doesn't exist."""
    repository = SQLAlchemyTemplateRepository(db_session)
    template = create_test_template()
    repository.save(template)

    result = repository.get_version(template.id, 999)
    assert result is None, "Should return None for nonexistent version"


def test_template_version_tracking(db_session: Session) -> None:
    """Test that removed fields are properly tracked across versions."""
    repository = SQLAlchemyTemplateRepository(db_session)
    template = create_test_template()
    repository.save(template)

    # Add a field
    v2 = template.evolve(
        new_fields={
            "contact_info": {
                "email": FieldDefinition(
                    name="email", type="email", description="Email address"
                )
            }
        }
    )
    repository.save(v2)

    # Remove the field
    v3 = v2.evolve(removed_fields={"contact_info": ["email"]})
    repository.save(v3)

    # Get all versions
    versions = repository.get_versions(template.id)

    # First version has no removed fields
    assert not versions[0].removed_fields

    # Second version has no removed fields
    assert not versions[1].removed_fields

    # Third version tracks the removed field
    assert "contact_info" in versions[2].removed_fields
    assert "email" in versions[2].removed_fields["contact_info"]
