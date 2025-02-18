# Backend Test Patterns

## Overview
This document details specific test patterns discovered and standardized during the implementation of our business objects. It serves as a companion to the general `TESTING.md` guide, providing concrete patterns and examples.

## Timezone Test Patterns

### Context & Discovery
These patterns were initially discovered during Note BO implementation (see CR-2024.02-23) and have been established as our standard approach for all timezone-aware business objects.

### Core Patterns

#### 1. UTC Storage Pattern
```python
def test_timestamp_stored_as_utc(db_session: Session) -> None:
    """Verify timestamps are always stored in UTC regardless of input timezone."""
    local_time = datetime.now(tz=ZoneInfo("Europe/Berlin"))
    note = Note(
        title="Test Note",
        content="Content",
        created_at=local_time
    )
    db_session.add(note)
    db_session.commit()

    # Verify stored in UTC
    stored_note = db_session.get(Note, note.id)
    assert stored_note.created_at.tzinfo == timezone.utc
    assert stored_note.created_at == local_time.astimezone(timezone.utc)
```

#### 2. DST-Aware Comparison Pattern
```python
def test_timestamp_comparison_across_dst(db_session: Session) -> None:
    """Verify timestamp comparisons work correctly across DST boundaries."""
    # Use moment-based comparisons instead of hard-coded hours
    winter_time = datetime(2024, 1, 1, 10, 0, tzinfo=ZoneInfo("Europe/Berlin"))
    summer_time = datetime(2024, 7, 1, 10, 0, tzinfo=ZoneInfo("Europe/Berlin"))

    note_winter = Note(title="Winter Note", created_at=winter_time)
    note_summer = Note(title="Summer Note", created_at=summer_time)

    db_session.add_all([note_winter, note_summer])
    db_session.commit()

    # Compare moments in time rather than wall clock times
    stored_winter = db_session.get(Note, note_winter.id)
    stored_summer = db_session.get(Note, note_summer.id)

    assert stored_winter.created_at < stored_summer.created_at
    assert (stored_summer.created_at - stored_winter.created_at).days == 181
```

#### 3. Timezone Preservation Pattern
```python
def test_timezone_info_preserved_in_conversions(db_session: Session) -> None:
    """Verify timezone information is preserved through save/load cycles."""
    original_tz = ZoneInfo("Asia/Tokyo")
    tokyo_time = datetime.now(tz=original_tz)

    note = Note(title="Tokyo Note", created_at=tokyo_time)
    db_session.add(note)
    db_session.commit()

    stored_note = db_session.get(Note, note.id)
    # Should be in UTC in database
    assert stored_note.created_at.tzinfo == timezone.utc

    # Should convert back to original timezone correctly
    tokyo_time_restored = stored_note.created_at.astimezone(original_tz)
    assert tokyo_time_restored.tzinfo == original_tz
    assert tokyo_time_restored == tokyo_time
```

### Best Practices

1. **Always Use Timezone-Aware Datetimes**
   - Never use naive datetimes in tests
   - Always specify timezone info explicitly
   - Use `ZoneInfo` for reliable timezone handling

2. **Moment-Based Comparisons**
   - Compare moments in time, not wall clock times
   - Account for DST transitions in comparisons
   - Use timedelta for duration calculations

3. **Explicit Timezone Conversions**
   - Always be explicit about timezone conversions
   - Verify both storage and retrieval preserve timezone info
   - Test with multiple different timezones

### Implementation Checklist

For each Business Object with timestamp fields:

- [ ] Implement UTC storage tests
- [ ] Implement DST handling tests
- [ ] Implement timezone preservation tests
- [ ] Verify timezone-aware query operations
- [ ] Test timezone conversions in API layer

### Related Documentation
- See `TESTING.md` for general testing guidelines
- See `MODEL_LAYER.md` for ORM implementation details
- See CR-2024.02-23 for original pattern discovery and rationale
