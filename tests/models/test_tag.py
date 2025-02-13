"""Tests for the Tag domain model."""
import pytest
from datetime import datetime, UTC, timedelta
from uuid import UUID
from backend.app.models.tag import Tag, EntityType


TEST_UUID = UUID("11111111-1111-1111-1111-111111111111")


def test_tag_creation():
    """Test creating a tag with basic properties.

    A tag must have:
    1. An entity_id (UUID) identifying what it's attached to
    2. An entity_type (contact, note, statement) identifying what kind of thing it's attached to
    3. A name that starts with '#' and is stored lowercase
    """
    # Create tag with minimum required fields
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#TEST"  # Using uppercase to test case normalization
    )

    # Verify initial state
    assert tag.entity_id == TEST_UUID
    assert tag.entity_type == EntityType.CONTACT
    assert tag.name == "#test"  # Should be lowercase
    assert tag.frequency_days is None  # No reminder frequency by default
    assert tag.last_contact is None  # No last contact by default


def test_tag_name_validation():
    """Test tag name validation rules.

    Tag names must:
    1. Start with '#'
    2. Be non-empty after the '#'
    3. Only contain letters, numbers, and underscores
    """
    # Test missing #
    with pytest.raises(ValueError, match="Tag name must start with '#'"):
        Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="test")

    # Test empty after #
    with pytest.raises(ValueError, match="Tag name cannot be empty"):
        Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="#")

    # Test invalid characters
    with pytest.raises(ValueError, match="Tag name can only contain letters, numbers, and underscores"):
        Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="#test@invalid")

    with pytest.raises(ValueError, match="Tag name can only contain letters, numbers, and underscores"):
        Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="#test space")


def test_tag_frequency_setting():
    """Test setting and validating reminder frequency.

    Frequency rules:
    1. Can be None (no reminders)
    2. Must be between 1 and 365 days
    3. Setting frequency should update last_contact
    4. Clearing frequency should clear last_contact
    """
    tag = Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="#test")

    # Initially no frequency
    assert tag.frequency_days is None
    assert tag.last_contact is None

    # Set valid frequency
    tag.set_frequency(7)  # Weekly
    assert tag.frequency_days == 7
    assert tag.last_contact is not None  # Should set last_contact

    # Clear frequency
    tag.set_frequency(None)
    assert tag.frequency_days is None
    assert tag.last_contact is None  # Should clear last_contact

    # Test invalid frequencies
    with pytest.raises(ValueError, match="Frequency must be between 1 and 365 days"):
        tag.set_frequency(0)  # Too low

    with pytest.raises(ValueError, match="Frequency must be between 1 and 365 days"):
        tag.set_frequency(366)  # Too high


def test_tag_staleness_calculation():
    """Test tag staleness calculation.

    A tag is stale if:
    1. It has a frequency set (not None)
    2. It has a last_contact date
    3. Time since last_contact > frequency_days
    """
    tag = Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="#test")

    # No frequency set - should not be stale
    assert not tag.is_stale()

    # Set frequency but no last_contact - should not be stale
    tag.set_frequency(7)  # Weekly
    assert not tag.is_stale()

    # Set last_contact to now - should not be stale
    now = datetime.now(UTC)
    tag.update_last_contact(now)
    assert not tag.is_stale()

    # Set last_contact to 8 days ago - should be stale
    tag.update_last_contact(now - timedelta(days=8))
    assert tag.is_stale()


def test_tag_last_contact_update():
    """Test updating the last contact timestamp.

    Last contact rules:
    1. Can be set to None to clear
    2. Can be set to specific timestamp
    3. Defaults to current time if no timestamp provided
    """
    tag = Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="#test")
    tag.set_frequency(7)  # Need frequency for meaningful last_contact

    # Update with current time
    tag.update_last_contact()
    assert tag.last_contact is not None
    assert (datetime.now(UTC) - tag.last_contact).total_seconds() < 1  # Almost equal

    # Update with specific time
    specific_time = datetime.now(UTC) - timedelta(days=3)
    tag.update_last_contact(specific_time)
    assert tag.last_contact == specific_time
