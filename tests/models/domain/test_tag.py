"""Tests for the Tag domain model."""

import pytest
from datetime import datetime, UTC, timedelta, timezone, time
from uuid import UUID
from zoneinfo import ZoneInfo
from backend.app.models.domain.tag_model import Tag, EntityType
import time as time_module  # Import time module for sleep


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
        name="#TEST",  # Using uppercase to test case normalization
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
        Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="test")

    # Test empty name
    with pytest.raises(ValueError, match="Tag name cannot be empty"):
        Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="#")

    # Test invalid characters
    error_msg = "Tag name can only contain letters, numbers, and underscores"
    with pytest.raises(ValueError, match=error_msg):
        Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="#test!")

    # Test case normalization
    tag = Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="#TEST_123")
    assert tag.name == "#test_123"


def test_tag_frequency():
    """Test setting and validating tag frequency.

    Frequency rules:
    1. Must be between 1 and 365 days
    2. Setting frequency initializes last_contact
    3. Clearing frequency clears last_contact
    """
    tag = Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="#test")

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
    tag = Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="#test")
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
    tag = Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="#test")

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


def test_tag_interaction_handling():
    """Test handling of note interactions.

    Interaction handling rules:
    1. Only contact tags should update last_contact
    2. Only update if is_interaction is True and has interaction_date
    3. Last contact should update to interaction_date
    4. Non-contact tags should not update
    """
    # Test contact tag with interaction
    contact_tag = Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="#test")
    interaction_time = datetime.now(UTC)
    contact_tag.handle_note_interaction(True, interaction_time)
    assert contact_tag.last_contact == interaction_time

    # Test contact tag without interaction
    contact_tag.last_contact = None
    contact_tag.handle_note_interaction(False, interaction_time)
    assert contact_tag.last_contact is None

    # Test contact tag with interaction but no date
    contact_tag.handle_note_interaction(True, None)
    assert contact_tag.last_contact is None

    # Test non-contact tags (should not update)
    note_tag = Tag(entity_id=TEST_UUID, entity_type=EntityType.NOTE, name="#test")
    statement_tag = Tag(entity_id=TEST_UUID, entity_type=EntityType.STATEMENT, name="#test")

    note_tag.handle_note_interaction(True, interaction_time)
    statement_tag.handle_note_interaction(True, interaction_time)

    assert note_tag.last_contact is None
    assert statement_tag.last_contact is None


def test_tag_timezone_validation():
    """Test timezone validation for datetime fields.

    Timezone rules:
    1. All datetime fields must be timezone-aware
    2. Naive datetimes are rejected
    3. Non-UTC timezones are converted to UTC
    4. DST transitions are handled correctly
    """
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#test"
    )
    tag.set_frequency(7)  # Enable frequency tracking

    # Test naive datetime rejection
    naive_dt = datetime.now()
    with pytest.raises(
        ValueError,
        match="must be timezone-aware"
    ):
        tag.update_last_contact(naive_dt)

    # Test UTC timezone acceptance
    utc_dt = datetime.now(UTC)
    tag.update_last_contact(utc_dt)
    assert tag.last_contact == utc_dt
    assert tag.last_contact.tzinfo == UTC  # type: ignore

    # Test non-UTC timezone conversion
    est = timezone(timedelta(hours=-5))
    est_dt = datetime.now(est)
    tag.update_last_contact(est_dt)

    # Verify UTC conversion
    expected_utc = est_dt.astimezone(UTC)
    assert tag.last_contact == expected_utc  # type: ignore
    assert tag.last_contact.tzinfo == UTC  # type: ignore

    # Test DST transition handling
    est_dst = timezone(timedelta(hours=-4))  # EDT
    dst_dt = datetime.now(est_dst)
    tag.update_last_contact(dst_dt)

    # Verify UTC conversion for DST
    expected_utc = dst_dt.astimezone(UTC)
    assert tag.last_contact == expected_utc  # type: ignore
    assert tag.last_contact.tzinfo == UTC  # type: ignore


def test_tag_timezone_staleness():
    """Test staleness calculations with different timezones.

    Staleness rules with timezones:
    1. Staleness is calculated using UTC
    2. DST changes don't affect staleness
    3. Different input timezones yield same staleness result
    """
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#test"
    )
    tag.set_frequency(7)  # Weekly

    # Base time in different timezones
    utc_time = datetime(2024, 1, 1, tzinfo=UTC)
    est = timezone(timedelta(hours=-5))
    est_time = utc_time.astimezone(est)
    ist = timezone(timedelta(hours=5, minutes=30))  # India
    ist_time = utc_time.astimezone(ist)

    # Test staleness calculation is consistent across timezones
    for test_time in [utc_time, est_time, ist_time]:
        tag.update_last_contact(test_time)

        # Mock current time to 6 days later (not stale)
        def mock_now() -> datetime:
            return test_time + timedelta(days=6)

        original_now = Tag.get_current_time
        Tag.get_current_time = staticmethod(mock_now)  # type: ignore
        try:
            assert not tag.is_stale()
        finally:
            Tag.get_current_time = original_now  # type: ignore

        # Mock current time to 8 days later (stale)
        def mock_now_stale() -> datetime:
            return test_time + timedelta(days=8)

        Tag.get_current_time = staticmethod(mock_now_stale)  # type: ignore
        try:
            assert tag.is_stale()
        finally:
            Tag.get_current_time = original_now  # type: ignore


def test_tag_timezone_interaction_handling():
    """Test interaction handling with different timezones.

    Interaction rules with timezones:
    1. Interaction times must be timezone-aware
    2. Different input timezones are normalized to UTC
    3. DST transitions are handled correctly
    """
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#test"
    )

    # Test with different timezones
    utc_time = datetime(2024, 1, 1, tzinfo=UTC)
    est = timezone(timedelta(hours=-5))
    est_time = utc_time.astimezone(est)
    ist = timezone(timedelta(hours=5, minutes=30))
    ist_time = utc_time.astimezone(ist)

    # All should result in same UTC time
    for test_time in [utc_time, est_time, ist_time]:
        tag.handle_note_interaction(True, test_time)
        assert tag.last_contact == utc_time  # type: ignore

    # Test DST transition
    est_winter = timezone(timedelta(hours=-5))
    est_summer = timezone(timedelta(hours=-4))

    winter_time = datetime(2024, 1, 1, tzinfo=est_winter)
    summer_time = datetime(2024, 7, 1, tzinfo=est_summer)

    # Both should convert to correct UTC
    tag.handle_note_interaction(True, winter_time)
    expected_utc = winter_time.astimezone(UTC)
    assert tag.last_contact == expected_utc  # type: ignore

    tag.handle_note_interaction(True, summer_time)
    expected_utc = summer_time.astimezone(UTC)
    assert tag.last_contact == expected_utc  # type: ignore

    # Test naive datetime rejection
    with pytest.raises(
        ValueError,
        match="must be timezone-aware"
    ):
        tag.handle_note_interaction(True, datetime.now())


def test_tag_timezone_boundary_cases():
    """Test timezone handling at day boundaries.

    Boundary rules:
    1. Day transitions are handled correctly across timezones
    2. DST transitions at midnight are handled
    3. Date comparisons work across timezone boundaries
    """
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#test"
    )
    tag.set_frequency(7)  # Weekly

    # Test day boundary handling
    ny_tz = ZoneInfo("America/New_York")
    tokyo_tz = ZoneInfo("Asia/Tokyo")

    # Create timestamps at different ends of day
    ny_end_of_day = datetime.combine(
        datetime.now(ny_tz).date(),
        time(23, 59, 59),
        tzinfo=ny_tz
    )
    tokyo_start_of_day = datetime.combine(
        (datetime.now(tokyo_tz) + timedelta(days=1)).date(),
        time(0, 0, 0),
        tzinfo=tokyo_tz
    )

    # Verify correct day boundary handling
    tag.update_last_contact(ny_end_of_day)
    ny_utc = tag.last_contact

    tag.update_last_contact(tokyo_start_of_day)
    tokyo_utc = tag.last_contact

    # Different wall times but close in UTC
    assert abs(ny_utc - tokyo_utc) < timedelta(days=1)  # type: ignore

    # Test DST boundary
    # Use exact times to ensure consistent behavior
    ny_before_dst = datetime(
        2024, 3, 10, 1, 0, tzinfo=ny_tz
    )  # Exactly 1:00 AM before spring forward
    ny_after_dst = datetime(
        2024, 3, 10, 3, 0, tzinfo=ny_tz
    )  # Exactly 3:00 AM after spring forward

    # Verify DST handling at boundary
    tag.update_last_contact(ny_before_dst)
    before_utc = tag.last_contact

    tag.update_last_contact(ny_after_dst)
    after_utc = tag.last_contact

    # Should be 1 hour difference in UTC
    # Use total_seconds() for more precise comparison
    time_diff = after_utc - before_utc  # type: ignore
    assert abs(time_diff.total_seconds() - 3600) < 1  # Within 1 second of an hour


def test_tag_timezone_sorting():
    """Test timezone handling in sorting and comparison.

    Sorting rules:
    1. Timestamps are compared in UTC
    2. Wall time differences are normalized
    3. DST transitions don't affect ordering
    """
    # Create tags with different timezone timestamps
    ny_tz = ZoneInfo("America/New_York")
    tokyo_tz = ZoneInfo("Asia/Tokyo")
    utc_tz = UTC

    base_time = datetime(2024, 1, 1, 12, 0, tzinfo=utc_tz)

    tags = [
        Tag(
            entity_id=TEST_UUID,
            entity_type=EntityType.CONTACT,
            name=f"#tag_{i}"
        )
        for i in range(3)
    ]

    # Set last_contact in different timezones but same UTC time
    tags[0].update_last_contact(base_time)
    tags[1].update_last_contact(base_time.astimezone(ny_tz))
    tags[2].update_last_contact(base_time.astimezone(tokyo_tz))

    # All should compare as equal
    assert (
        tags[0].last_contact == tags[1].last_contact ==
        tags[2].last_contact
    )

    # Test sorting with DST transitions
    ny_winter = datetime(2024, 1, 1, 12, tzinfo=ny_tz)
    ny_summer = datetime(2024, 7, 1, 12, tzinfo=ny_tz)

    tags[0].update_last_contact(ny_winter)
    tags[1].update_last_contact(ny_summer)

    # Summer time should be later despite same wall time
    assert tags[0].last_contact < tags[1].last_contact  # type: ignore


def test_tag_timezone_query_patterns():
    """Test timezone handling in query-like operations.

    Query rules:
    1. Range queries work across timezone boundaries
    2. Frequency calculations handle timezone transitions
    3. Staleness checks work across DST changes
    """
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#test"
    )
    tag.set_frequency(7)  # Weekly

    ny_tz = ZoneInfo("America/New_York")

    # Test range handling across DST
    # Use a fixed time to avoid test flakiness
    spring_forward = datetime(2024, 3, 10, 2, 0, tzinfo=ny_tz)

    # Before DST change (6 days ago)
    six_days_ago = spring_forward - timedelta(days=6)
    tag.update_last_contact(six_days_ago)

    # Mock current time to exactly 6 days later
    def mock_current_time() -> datetime:
        return six_days_ago + timedelta(days=6)

    original_now = Tag.get_current_time
    Tag.get_current_time = classmethod(lambda cls: mock_current_time())  # type: ignore
    try:
        assert not tag.is_stale()  # Still within 7 days
    finally:
        Tag.get_current_time = original_now  # type: ignore

    # After DST change (1 day ahead)
    one_day_ahead = spring_forward + timedelta(days=1)
    tag.update_last_contact(one_day_ahead)

    # Mock current time to 6 days after the new time
    def mock_future_time() -> datetime:
        return one_day_ahead + timedelta(days=6)

    Tag.get_current_time = classmethod(lambda cls: mock_future_time())  # type: ignore
    try:
        assert not tag.is_stale()  # DST shouldn't affect staleness
    finally:
        Tag.get_current_time = original_now  # type: ignore

    # Test frequency calculation across timezone changes
    tokyo_tz = ZoneInfo("Asia/Tokyo")
    current_tokyo = datetime.now(tokyo_tz)
    tag.update_last_contact(current_tokyo)

    # Mock current time to exactly 6 days after Tokyo time
    def mock_ny_time() -> datetime:
        return current_tokyo + timedelta(days=6)

    Tag.get_current_time = classmethod(lambda cls: mock_ny_time())  # type: ignore
    try:
        assert not tag.is_stale()  # Timezone difference shouldn't affect staleness
    finally:
        Tag.get_current_time = original_now  # type: ignore


def test_tag_audit_field_timezone_handling():
    """Test timezone handling for audit fields.

    Rules:
    1. created_at is always in UTC
    2. updated_at is always in UTC
    3. updated_at changes with state modifications
    4. Timezone info is preserved through updates
    """
    # Create tag and verify initial timestamps
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#test"
    )

    # Verify UTC timezone
    assert tag.created_at.tzinfo == UTC
    assert tag.updated_at.tzinfo == UTC

    # Test frequency update changes timestamp
    original_updated_at = tag.updated_at
    time_module.sleep(0.001)  # Ensure timestamp difference
    tag.set_frequency(7)
    assert tag.updated_at > original_updated_at
    assert tag.updated_at.tzinfo == UTC

    # Test last_contact update changes timestamp
    original_updated_at = tag.updated_at
    time_module.sleep(0.001)
    tag.update_last_contact()
    assert tag.updated_at > original_updated_at
    assert tag.updated_at.tzinfo == UTC

    # Test timezone conversion
    ny_tz = ZoneInfo("America/New_York")
    ny_time = datetime.now(ny_tz)

    original_updated_at = tag.updated_at
    time_module.sleep(0.001)
    tag.update_last_contact(ny_time)
    assert tag.updated_at > original_updated_at
    assert tag.updated_at.tzinfo == UTC
    assert tag.last_contact == ny_time.astimezone(UTC)
