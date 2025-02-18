"""Tests for the Contact domain model.

Tests are organized by complexity and frequency of use:
1. Basic Tests - Creation and validation
2. Data Structure Tests - Complex object validation
3. Relationship Tests - Tag and note management
4. State Management Tests - Interaction tracking
5. Temporal Tests - Timezone handling
"""

import pytest
from datetime import datetime, UTC, timezone, timedelta
from uuid import UUID
from typing import Any, cast
from backend.app.models.domain.contact_model import Contact
from zoneinfo import ZoneInfo


TEST_UUID = UUID("11111111-1111-1111-1111-111111111111")


# region Basic Tests (Common)

def test_contact_creation():
    """Test basic contact creation with required and optional fields."""
    contact = Contact(name="Test Contact")
    assert contact.name == "Test Contact"
    assert contact.first_name is None
    assert contact.briefing_text is None
    assert contact.sub_information == {}
    assert contact.last_contact is None
    assert contact.contact_briefing_text is None
    assert contact.notes == []
    assert contact.tags == []

    # Test with all fields
    sub_info = {"family_status": "Married", "professional_situation": "CEO"}
    contact = Contact(
        name="John Doe",
        first_name="John",
        briefing_text="Important business contact",
        sub_information=sub_info,
    )
    assert contact.name == "John Doe"
    assert contact.first_name == "John"
    assert contact.briefing_text == "Important business contact"
    assert contact.sub_information == sub_info


def test_contact_sub_information_validation():
    """Test sub_information validation rules."""
    # Test invalid type
    with pytest.raises(ValueError):
        Contact(name="John Doe", sub_information=cast(Any, "invalid"))

    # Test default empty dict
    contact = Contact(name="John Doe")
    assert contact.sub_information == {}

    # Test nested dictionary
    sub_info = {
        "personal": {
            "hobbies": ["reading", "hiking"],
            "family": {"status": "married", "children": 2},
        },
        "professional": {"role": "developer", "skills": ["python", "typescript"]},
    }
    contact = Contact(name="John Doe", sub_information=sub_info)
    assert contact.sub_information == sub_info


# endregion


# region Relationship Tests (Common)

def test_contact_tag_management():
    """Test tag relationship management.

    Rules:
    1. Tag addition with validation
    2. Tag format rules
    3. Case normalization
    4. Duplicate prevention
    5. Tag removal
    """
    contact = Contact(name="John Doe")

    # Add valid tags
    contact.add_tag("#test")
    contact.add_tag("#project")

    assert len(contact.tags) == 2
    assert "#test" in [t.name for t in contact.tags]
    assert "#project" in [t.name for t in contact.tags]

    # Test invalid tag format
    with pytest.raises(ValueError, match="Tag must start with #"):
        contact.add_tag("invalid")

    # Test duplicate tag
    contact.add_tag("#test")  # Should be ignored
    assert len(contact.tags) == 2

    # Test case normalization
    contact.add_tag("#TEST")  # Should be normalized to #test
    assert len(contact.tags) == 2

    # Remove tag
    test_tag = next(t for t in contact.tags if t.name == "#test")
    contact.remove_tag(test_tag)
    assert len(contact.tags) == 1
    assert "#test" not in [t.name for t in contact.tags]


def test_contact_note_management():
    """Test note relationship management.

    Rules:
    1. Note addition with validation
    2. Order preservation
    3. Note removal
    4. Content validation
    """
    contact = Contact(name="John Doe")

    # Add notes
    note1 = contact.add_note("First note")
    note2 = contact.add_note("Second note")

    assert len(contact.notes) == 2
    assert contact.notes[0] is note1
    assert contact.notes[1] is note2
    assert note1.content == "First note"
    assert note2.content == "Second note"

    # Test empty note
    with pytest.raises(ValueError, match="Content notes require content"):
        contact.add_note("")

    # Test whitespace note
    with pytest.raises(ValueError, match="Content notes require content"):
        contact.add_note("   ")

    # Remove note
    contact.remove_note(note1)
    assert len(contact.notes) == 1
    assert contact.notes[0] is note2
    assert contact.notes[0].content == "Second note"


# endregion


# region State Management Tests (Moderate)

def test_contact_interaction_recording():
    """Test state changes from interactions.

    Rules:
    1. Note creation
    2. Timestamp updates
    3. Briefing updates
    4. State consistency
    """
    contact = Contact(name="Test Contact")
    interaction_time = datetime.now(UTC)

    # Record interaction with content
    note = contact.add_interaction(
        content="Met for coffee",
        interaction_date=interaction_time
    )

    assert note.is_interaction
    assert note.interaction_date == interaction_time
    assert note.content == "Met for coffee"
    assert contact.last_contact == interaction_time
    assert contact.contact_briefing_text == "Met for coffee"

    # Record interaction without content
    new_time = datetime.now(UTC)
    note = contact.add_interaction(interaction_date=new_time)

    assert note.is_interaction
    assert note.interaction_date == new_time
    assert note.content is None
    assert contact.last_contact == new_time
    assert contact.contact_briefing_text == "Met for coffee"  # Shouldn't change without content


def test_contact_tag_interaction_updates():
    """Test cascading state updates.

    Rules:
    1. Tag timestamp updates
    2. State propagation
    3. State consistency
    """
    contact = Contact(name="Test Contact")
    contact.add_tag("#test")
    contact.add_tag("#monthly")

    # Record interaction
    interaction_time = datetime.now(UTC)
    contact.add_interaction(
        content="Test interaction",
        interaction_date=interaction_time
    )

    # Verify all tags updated
    for tag in contact.tags:
        assert tag.last_contact == interaction_time


def test_invalid_interaction_recording():
    """Test interaction state validation.

    Rules:
    1. Required fields
    2. Time constraints
    3. Content validation
    4. State rules
    """
    contact = Contact(name="Test Contact")

    # Test missing date
    with pytest.raises(ValueError, match="Interaction notes require a date"):
        contact.add_interaction()

    # Test future date
    future_time = datetime.now(UTC).replace(year=9999)
    with pytest.raises(ValueError, match="Interaction date cannot be in the future"):
        contact.add_interaction(interaction_date=future_time)

    # Test empty content (should be allowed for interactions)
    interaction_time = datetime.now(UTC)
    note = contact.add_interaction(interaction_date=interaction_time)
    assert note.content is None


# endregion


# region Temporal Tests (Complex)

def test_contact_timezone_handling():
    """Test timezone handling.

    Rules:
    1. Timezone-aware input
    2. UTC conversion
    3. Timezone info
    4. Input validation
    """
    # Test with UTC time
    utc_time = datetime.now(UTC)
    contact = Contact(name="Test Contact")
    contact.add_interaction(interaction_date=utc_time)
    assert contact.last_contact is not None
    assert contact.last_contact == utc_time
    assert contact.last_contact.tzinfo == UTC

    # Test with different timezone (Tokyo)
    tokyo_time = datetime.now(ZoneInfo("Asia/Tokyo"))
    contact.add_interaction(interaction_date=tokyo_time)
    assert contact.last_contact is not None
    assert contact.last_contact == tokyo_time.astimezone(UTC)
    assert contact.last_contact.tzinfo == UTC

    # Test with custom timezone offset
    custom_tz = timezone(timedelta(hours=5, minutes=30))  # UTC+5:30
    custom_time = datetime.now(custom_tz)
    contact.add_interaction(interaction_date=custom_time)
    assert contact.last_contact is not None
    assert contact.last_contact == custom_time.astimezone(UTC)
    assert contact.last_contact.tzinfo == UTC

    # Test rejection of naive datetime
    naive_time = datetime.now()
    with pytest.raises(ValueError, match="Interaction date must be timezone-aware"):
        contact.add_interaction(interaction_date=naive_time)


def test_contact_timezone_preservation():
    """Test timezone consistency.

    Rules:
    1. Multi-timezone ops
    2. DST handling
    3. Timezone conversion
    4. State consistency
    """
    contact = Contact(name="Test Contact")

    # Test multiple interactions
    times = [
        datetime.now(ZoneInfo("America/New_York")),
        datetime.now(ZoneInfo("Europe/London")),
        datetime.now(ZoneInfo("Asia/Tokyo")),
    ]

    for time in times:
        contact.add_interaction(interaction_date=time)
        assert contact.last_contact is not None
        assert contact.last_contact == time.astimezone(UTC)
        assert contact.last_contact.tzinfo == UTC

    # Test DST transition
    ny_tz = ZoneInfo("America/New_York")
    winter_time = datetime(2024, 1, 1, 12, 0, tzinfo=ny_tz)  # During EST
    summer_time = datetime(2024, 7, 1, 12, 0, tzinfo=ny_tz)  # During EDT

    contact.add_interaction(interaction_date=winter_time)
    assert contact.last_contact is not None
    assert contact.last_contact == winter_time.astimezone(UTC)

    contact.add_interaction(interaction_date=summer_time)
    assert contact.last_contact is not None
    assert contact.last_contact == summer_time.astimezone(UTC)


# endregion
