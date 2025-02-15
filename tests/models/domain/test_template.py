"""Test cases for the template domain model."""

import pytest
from datetime import datetime, UTC
from uuid import uuid4
from backend.app.models.domain.template_model import (
    FieldDefinition,
    CategoryDefinition,
    Template,
)


def test_field_definition_creation():
    """Test creating a field definition with all properties."""
    field = FieldDefinition(
        name="phone",
        type="phone",
        description="Contact phone number",
        display_format="+1 XXX-XXX-XXXX",
        reminder_template="Call {name} at {phone}",
        validators=[],
    )

    assert field.name == "phone"
    assert field.type == "phone"
    assert field.description == "Contact phone number"
    assert field.display_format == "+1 XXX-XXX-XXXX"
    assert field.reminder_template == "Call {name} at {phone}"
    assert field.validators == []


def test_field_definition_required_only():
    """Test creating a field definition with only required fields."""
    field = FieldDefinition(name="notes", type="string", description="Additional notes")

    assert field.name == "notes"
    assert field.type == "string"
    assert field.description == "Additional notes"
    assert field.display_format is None
    assert field.reminder_template is None
    assert field.validators == []


def test_category_definition_creation():
    """Test creating a category with multiple fields."""
    category = CategoryDefinition(
        name="contact_info",
        description="Basic contact information",
        fields={
            "phone": FieldDefinition(
                name="phone", type="phone", description="Contact phone number"
            ),
            "email": FieldDefinition(
                name="email", type="email", description="Email address"
            ),
        },
    )

    assert category.name == "contact_info"
    assert category.description == "Basic contact information"
    assert len(category.fields) == 2
    assert all(isinstance(f, FieldDefinition) for f in category.fields.values())


def test_template_creation():
    """Test creating a template with categories and version."""
    template_id = uuid4()
    now = datetime.now(UTC)

    template = Template(
        id=template_id,
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

    assert template.id == template_id
    assert template.version == 1
    assert len(template.categories) == 1
    assert isinstance(template.categories["contact_info"], CategoryDefinition)


def test_template_validation_success():
    """Test successful validation of sub_information against template."""
    now = datetime.now(UTC)
    template = Template(
        id=uuid4(),
        categories={
            "contact_info": CategoryDefinition(
                name="contact_info",
                description="Basic contact information",
                fields={
                    "phone": FieldDefinition(
                        name="phone", type="phone", description="Phone number"
                    ),
                    "email": FieldDefinition(
                        name="email", type="email", description="Email address"
                    ),
                    "birthday": FieldDefinition(
                        name="birthday", type="date", description="Date of birth"
                    ),
                    "notes": FieldDefinition(
                        name="notes", type="string", description="Additional notes"
                    ),
                },
            )
        },
        version=1,
        created_at=now,
        updated_at=now,
    )

    valid_data = {
        "contact_info": {
            "phone": "+1 555-555-5555",
            "email": "test@example.com",
            "birthday": "1990-01-01",
            "notes": "Some free text notes",
        }
    }

    assert template.validate_data(valid_data) is True


def test_template_validation_failures():
    """Test various validation failures."""
    now = datetime.now(UTC)
    template = Template(
        id=uuid4(),
        categories={
            "contact_info": CategoryDefinition(
                name="contact_info",
                description="Basic contact information",
                fields={
                    "phone": FieldDefinition(
                        name="phone", type="phone", description="Phone number"
                    ),
                    "email": FieldDefinition(
                        name="email", type="email", description="Email address"
                    ),
                    "birthday": FieldDefinition(
                        name="birthday", type="date", description="Date of birth"
                    ),
                },
            )
        },
        version=1,
        created_at=now,
        updated_at=now,
    )

    # Test invalid phone format
    with pytest.raises(ValueError) as exc_info:
        template.validate_data({"contact_info": {"phone": "invalid-phone"}})
    assert "phone" in str(exc_info.value)
    assert "valid phone number" in str(exc_info.value)

    # Test invalid email format
    with pytest.raises(ValueError) as exc_info:
        template.validate_data({"contact_info": {"email": "not-an-email"}})
    assert "email" in str(exc_info.value)
    assert "valid email" in str(exc_info.value)

    # Test invalid date format
    with pytest.raises(ValueError) as exc_info:
        template.validate_data({"contact_info": {"birthday": "not-a-date"}})
    assert "birthday" in str(exc_info.value)
    assert "ISO date" in str(exc_info.value)


def test_template_get_filled_fields():
    """Test getting only filled fields from sub_information."""
    now = datetime.now(UTC)
    template = Template(
        id=uuid4(),
        categories={
            "contact_info": CategoryDefinition(
                name="contact_info",
                description="Basic contact information",
                fields={
                    "phone": FieldDefinition(
                        name="phone", type="phone", description="Phone number"
                    ),
                    "email": FieldDefinition(
                        name="email", type="email", description="Email address"
                    ),
                    "notes": FieldDefinition(
                        name="notes", type="string", description="Additional notes"
                    ),
                },
            )
        },
        version=1,
        created_at=now,
        updated_at=now,
    )

    data = {
        "contact_info": {"phone": "+1 555-555-5555", "email": "", "notes": "Some notes"}
    }

    filled_fields = template.get_filled_fields(data)
    assert "phone" in filled_fields["contact_info"]
    assert "notes" in filled_fields["contact_info"]
    assert "email" not in filled_fields["contact_info"]


def test_template_evolution_add_field():
    """Test adding a new field to an existing template."""
    now = datetime.now(UTC)
    old_template = Template(
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

    # Create new version with added field
    new_template = old_template.evolve(
        new_fields={
            "contact_info": {
                "email": FieldDefinition(
                    name="email", type="email", description="Email address"
                )
            }
        }
    )

    # Check version increment
    assert new_template.version == old_template.version + 1

    # Check old field preserved
    assert "phone" in new_template.categories["contact_info"].fields

    # Check new field added
    assert "email" in new_template.categories["contact_info"].fields

    # Validate old data still works
    old_data = {"contact_info": {"phone": "+1 555-555-5555"}}
    assert new_template.validate_data(old_data) is True


def test_template_evolution_remove_field():
    """Test removing a field while preserving historical data."""
    now = datetime.now(UTC)
    old_template = Template(
        id=uuid4(),
        categories={
            "contact_info": CategoryDefinition(
                name="contact_info",
                description="Basic contact information",
                fields={
                    "phone": FieldDefinition(
                        name="phone", type="phone", description="Phone number"
                    ),
                    "fax": FieldDefinition(  # Field to be removed
                        name="fax", type="phone", description="Fax number"
                    ),
                },
            )
        },
        version=1,
        created_at=now,
        updated_at=now,
    )

    # Create new version without fax field
    new_template = old_template.evolve(removed_fields={"contact_info": ["fax"]})

    # Check version increment
    assert new_template.version == old_template.version + 1

    # Check fax field removed
    assert "fax" not in new_template.categories["contact_info"].fields

    # Check phone field preserved
    assert "phone" in new_template.categories["contact_info"].fields

    # Old data with removed field should still validate
    old_data = {
        "contact_info": {
            "phone": "+1 555-555-5555",
            "fax": "+1 555-555-5556",  # Historical data
        }
    }
    assert new_template.validate_data(old_data) is True


def test_template_evolution_change_field_type():
    """Test changing a field type with validation of old data."""
    now = datetime.now(UTC)
    old_template = Template(
        id=uuid4(),
        categories={
            "contact_info": CategoryDefinition(
                name="contact_info",
                description="Basic contact information",
                fields={
                    "birthday": FieldDefinition(
                        name="birthday",
                        type="string",  # Initially a string
                        description="Date of birth",
                    )
                },
            )
        },
        version=1,
        created_at=now,
        updated_at=now,
    )

    # Create new version with changed field type
    new_template = old_template.evolve(
        changed_fields={
            "contact_info": {
                "birthday": FieldDefinition(
                    name="birthday",
                    type="date",  # Changed to date type
                    description="Date of birth",
                )
            }
        }
    )

    # Check version increment
    assert new_template.version == old_template.version + 1

    # Check field type changed
    assert new_template.categories["contact_info"].fields["birthday"].type == "date"

    # Old string data should still validate if it's ISO format
    old_data = {"contact_info": {"birthday": "1990-01-01"}}  # Valid ISO date string
    assert new_template.validate_data(old_data) is True

    # Invalid date strings should fail
    with pytest.raises(ValueError):
        new_template.validate_data(
            {"contact_info": {"birthday": "Jan 1, 1990"}}  # Invalid format
        )
