import pytest
from datetime import datetime, UTC, timedelta
from backend.app.models.tag import Tag, EntityType
import uuid


TEST_UUID = uuid.UUID("11111111-1111-1111-1111-111111111111")


def test_tag_creation() -> None:
    """Test basic tag creation with required fields.

    A tag should:
    1. Have an entity_id (UUID)
    2. Have an entity_type (contact, note, or statement)
    3. Have a name that starts with '#'
    4. Store the name in lowercase
    5. Have optional frequency tracking fields (initially None)
    """
    # Create tag with minimum required fields
    tag = Tag(
        entity_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        entity_type=EntityType.CONTACT,
        name="#TEST"  # Using uppercase to test case normalization
    )

    # Verify initial state
    assert tag.name == "#test"  # Should be lowercase
    assert tag.entity_type == EntityType.CONTACT
    assert tag.frequency_days is None
    assert tag.last_contact is None


def test_tag_name_validation() -> None:
    """Test tag name validation.

    Tag names must:
    1. Start with '#'
    2. Be non-empty after the '#'
    """
    test_id = uuid.UUID("11111111-1111-1111-1111-111111111111")

    # Test invalid names
    with pytest.raises(ValueError, match="must start with '#'"):
        Tag(
            entity_id=test_id,
            entity_type=EntityType.CONTACT,
            name="invalid"  # Missing #
        )

    with pytest.raises(ValueError, match="must start with '#'"):
        Tag(
            entity_id=test_id,
            entity_type=EntityType.CONTACT,
            name=""  # Empty string
        )


def test_tag_case_normalization() -> None:
    """Test that tag names are normalized to lowercase."""
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#TEST"
    )
    assert tag.name == "#test"


def test_tag_frequency_tracking() -> None:
    """Test tracking frequency and staleness of tags."""
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#weekly"
    )

    # Set frequency and last contact
    tag.set_frequency(7)
    tag.update_last_contact()

    # Tag should not be stale yet
    assert not tag.is_stale()

    # Move last_contact to 8 days ago
    tag.update_last_contact(datetime.now(UTC) - timedelta(days=8))

    # Tag should now be stale
    assert tag.is_stale()
    assert tag.staleness_days == 1


def test_tag_frequency_validation() -> None:
    """Test validation of tag frequency settings."""
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#weekly"
    )

    # Test valid frequency range
    tag.set_frequency(1)  # Minimum valid frequency
    assert tag.frequency_days == 1
    tag.set_frequency(365)  # Maximum valid frequency
    assert tag.frequency_days == 365

    # Test invalid frequencies
    with pytest.raises(ValueError, match="between 1 and 365"):
        tag.set_frequency(0)
    with pytest.raises(ValueError, match="between 1 and 365"):
        tag.set_frequency(366)
    with pytest.raises(ValueError, match="between 1 and 365"):
        tag.set_frequency(-1)


def test_tag_last_contact_tracking() -> None:
    """Test tracking last contact date."""
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#weekly"
    )
    tag.set_frequency(7)

    # Update last contact with default (now)
    tag.update_last_contact()
    assert tag.last_contact is not None
    assert (datetime.now(UTC) - tag.last_contact).total_seconds() < 1

    # Update with specific date
    specific_date = datetime.now(UTC) - timedelta(days=3)
    tag.update_last_contact(specific_date)
    assert tag.last_contact == specific_date


def test_tag_frequency_disable() -> None:
    """Test disabling frequency tracking."""
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#weekly"
    )

    # Set initial frequency
    tag.set_frequency(7)
    tag.update_last_contact()
    assert tag.frequency_days == 7
    assert tag.last_contact is not None

    # Disable frequency tracking
    tag.disable_frequency()
    assert tag.frequency_days is None
    assert tag.last_contact is None
    assert not tag.is_stale()


def test_tag_basic_properties() -> None:
    """Test the most basic tag properties.

    A tag must have:
    1. An entity_id (UUID)
    2. An entity type (one of: contact, note, statement)
    3. A name that starts with '#'
    """
    tag = Tag(
        entity_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        entity_type=EntityType.CONTACT,
        name="#test"
    )

    assert tag.entity_id == uuid.UUID("11111111-1111-1111-1111-111111111111")
    assert tag.entity_type == EntityType.CONTACT
    assert tag.name == "#test"
