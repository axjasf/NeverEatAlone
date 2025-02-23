"""Test cases for the template domain model.

Tests are organized by complexity and frequency of use:
1. Basic Tests - Creation and simple validation
2. Data Structure Tests - Complex object validation
3. Temporal Tests - Timezone handling
4. Evolution Tests - Schema changes and migrations
"""

import pytest
from datetime import datetime, UTC
from uuid import uuid4
from backend.app.models.domain.template_model import (
    FieldDefinition,
    CategoryDefinition,
    Template,
)
from zoneinfo import ZoneInfo

# region Basic Tests (Common)

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

# endregion

# region Data Structure Tests (Complex)

def test_template_validation_success():
    """Test validation of complex nested data."""
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
    """Test validation failures for complex data."""
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
    """Test filtering and processing of nested data."""
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

# endregion

# region Temporal Tests (Complex)

def test_template_timezone_handling():
    """Test timezone handling in Template model.

    Verifies:
    1. Timezone-aware datetime requirements
    2. Timezone preservation during evolution
    3. UTC conversion for storage
    """
    template_id = uuid4()

    # Test with different input timezones
    tokyo_time = datetime.now(ZoneInfo("Asia/Tokyo"))
    ny_time = tokyo_time.astimezone(ZoneInfo("America/New_York"))  # Same moment, different zone

    # Test creation with timezone-aware datetime
    template = Template(
        id=template_id,
        categories={
            "test": CategoryDefinition(
                name="test",
                description="Test category",
                fields={
                    "field": FieldDefinition(
                        name="field",
                        type="string",
                        description="Test field"
                    )
                }
            )
        },
        version=1,
        created_at=tokyo_time,
        updated_at=ny_time
    )

    # Verify datetimes are stored in UTC and represent the same moment
    assert template.created_at.tzinfo == UTC
    assert template.updated_at.tzinfo == UTC
    assert template.created_at == tokyo_time.astimezone(UTC)
    assert template.updated_at == ny_time.astimezone(UTC)

    # Test rejection of naive datetime
    naive_time = datetime.now()
    with pytest.raises(ValueError, match="must be timezone-aware"):
        Template(
            id=template_id,
            categories={},
            version=1,
            created_at=naive_time,
            updated_at=naive_time
        )

    # Test timezone handling during evolution
    evolved = template.evolve(
        new_fields={
            "test": {
                "new_field": FieldDefinition(
                    name="new_field",
                    type="string",
                    description="New test field"
                )
            }
        }
    )

    # Verify evolved template preserves timezone awareness
    assert evolved.created_at.tzinfo == UTC
    assert evolved.updated_at.tzinfo == UTC
    assert evolved.version == template.version + 1

    # Test DST transition
    ny_tz = ZoneInfo("America/New_York")
    winter_time = datetime(2024, 1, 1, 12, 0, tzinfo=ny_tz)  # During EST
    summer_time = datetime(2024, 7, 1, 12, 0, tzinfo=ny_tz)  # During EDT

    winter_template = Template(
        id=uuid4(),
        categories={},
        version=1,
        created_at=winter_time,
        updated_at=winter_time
    )
    summer_template = Template(
        id=uuid4(),
        categories={},
        version=1,
        created_at=summer_time,
        updated_at=summer_time
    )

    # Verify DST handling
    assert winter_template.created_at == winter_time.astimezone(UTC)
    assert summer_template.created_at == summer_time.astimezone(UTC)

    # Test fractional offset (India UTC+5:30)
    india_tz = ZoneInfo("Asia/Kolkata")
    india_time = datetime(2024, 1, 1, 1, 0, tzinfo=india_tz)
    india_template = Template(
        id=uuid4(),
        categories={},
        version=1,
        created_at=india_time,
        updated_at=india_time
    )
    assert india_template.created_at == india_time.astimezone(UTC)

    # Test day boundary transition
    tokyo_tz = ZoneInfo("Asia/Tokyo")
    ny_midnight = datetime(2024, 1, 1, 0, 0, tzinfo=ny_tz)
    tokyo_time = ny_midnight.astimezone(tokyo_tz)

    ny_template = Template(
        id=uuid4(),
        categories={},
        version=1,
        created_at=ny_midnight,
        updated_at=ny_midnight
    )
    tokyo_template = Template(
        id=uuid4(),
        categories={},
        version=1,
        created_at=tokyo_time,
        updated_at=tokyo_time
    )

    # Verify both represent the same moment in UTC
    assert ny_template.created_at == tokyo_template.created_at

# endregion

# region Evolution Tests (Rare)

def test_template_evolution_add_field():
    """Test schema evolution: adding fields."""
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
    """Test schema evolution: removing fields."""
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
    """Test schema evolution: changing field types."""
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

# endregion
