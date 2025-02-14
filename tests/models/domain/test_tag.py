"""Tests for the Tag domain model."""
import pytest
from datetime import datetime, UTC, timedelta
from uuid import UUID
from backend.app.models.domain.tag import Tag, EntityType


TEST_UUID = UUID("11111111-1111-1111-1111-111111111111")


def test_tag_creation():
    """Test creating a tag with basic properties.

    A tag must have:
    1. An entity_id (UUID) identifying what it's attached to
    2. An entity_type (contact, note, statement) identifying what kind
       of thing it's attached to
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
    assert tag.entity_type == EntityType.CONTACT.value
    assert tag.name == "#test"  # Should be lowercase
    assert tag.frequency_days is None  # No reminder frequency by default
    assert tag.last_contact is None  # No last contact by default


def test_tag_name_validation():
    """Test tag name validation rules.

    Tag name rules:
    1. Must start with '#'
    2. Cannot be empty after '#'
    3. Can only contain letters, numbers, and underscores
    4. Is stored in lowercase
    """
    # Test missing '#'
    with pytest.raises(ValueError, match="Tag name must start with '#'"):
        Tag(
            entity_id=TEST_UUID,
            entity_type=EntityType.CONTACT,
            name="test"
        )

    # Test empty name
    with pytest.raises(ValueError, match="Tag name cannot be empty"):
        Tag(
            entity_id=TEST_UUID,
            entity_type=EntityType.CONTACT,
            name="#"
        )

    # Test invalid characters
    error_msg = "Tag name can only contain letters, numbers, and underscores"
    with pytest.raises(ValueError, match=error_msg):
        Tag(
            entity_id=TEST_UUID,
            entity_type=EntityType.CONTACT,
            name="#test!"
        )

    # Test case normalization
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#TEST_123"
    )
    assert tag.name == "#test_123"


def test_tag_frequency():
    """Test setting and validating tag frequency.

    Frequency rules:
    1. Must be between 1 and 365 days
    2. Setting frequency initializes last_contact
    3. Clearing frequency clears last_contact
    """
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#test"
    )

    # Test invalid frequencies
    error_msg = "Frequency must be between 1 and 365 days"
    with pytest.raises(ValueError, match=error_msg):
        tag.set_frequency(0)
    with pytest.raises(ValueError, match=error_msg):
        tag.set_frequency(366)

    # Test setting valid frequency
    tag.set_frequency(7)  # Weekly
    assert tag.frequency_days == 7
    assert tag.last_contact is not None  # Should be initialized

    # Test clearing frequency
    tag.set_frequency(None)
    assert tag.frequency_days is None
    assert tag.last_contact is None  # Should be cleared


def test_tag_last_contact():
    """Test updating last contact timestamp.

    Last contact rules:
    1. Can be updated with specific timestamp
    2. Defaults to current time if no timestamp provided
    3. Can be cleared by disabling frequency
    """
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#test"
    )
    tag.set_frequency(7)  # Enable frequency tracking

    # Test specific timestamp
    test_time = datetime(2024, 1, 1, tzinfo=UTC)
    tag.update_last_contact(test_time)
    assert tag.last_contact == test_time

    # Test current time
    before = datetime.now(UTC)
    tag.update_last_contact()
    after = datetime.now(UTC)
    assert before <= tag.last_contact <= after  # type: ignore

    # Test clearing via frequency
    tag.set_frequency(None)
    assert tag.last_contact is None


def test_tag_staleness():
    """Test checking if a tag is stale.

    Staleness rules:
    1. Only tags with frequency can be stale
    2. Tag is stale if time since last contact > frequency
    3. Uses current time for comparison
    """
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#test"
    )

    # No frequency = never stale
    assert not tag.is_stale()

    # Fresh tag
    tag.set_frequency(7)  # Weekly
    assert not tag.is_stale()

    # Stale tag (mock current time)
    test_time = datetime(2024, 1, 1, tzinfo=UTC)
    tag.update_last_contact(test_time)

    def mock_now() -> datetime:
        return test_time + timedelta(days=8)

    original_now = Tag.get_current_time
    Tag.get_current_time = staticmethod(mock_now)  # type: ignore
    try:
        assert tag.is_stale()
    finally:
        Tag.get_current_time = original_now  # type: ignore
