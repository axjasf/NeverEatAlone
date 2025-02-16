"""Tests for the Base domain model."""

from datetime import datetime, timezone, UTC
from uuid import UUID
from zoneinfo import ZoneInfo
from backend.app.models.domain.base_model import BaseModel
import pytest


def test_base_model_initialization():
    """Test base model initialization.

    Base model should:
    1. Generate a UUID on creation
    2. Set created_at timestamp
    3. Set updated_at equal to created_at initially
    4. Store all timestamps in UTC
    5. Accept timezone-aware datetimes
    6. Reject naive datetimes
    """
    # Test default initialization
    model = BaseModel()

    assert isinstance(model.id, UUID)
    assert isinstance(model.created_at, datetime)
    assert isinstance(model.updated_at, datetime)
    assert model.created_at.tzinfo == UTC  # Ensure UTC timezone
    assert model.updated_at == model.created_at

    # Test with timezone-aware datetime
    ny_time = datetime.now(ZoneInfo("America/New_York"))
    model = BaseModel(created_at=ny_time)
    assert model.created_at.tzinfo == UTC
    assert model.created_at == ny_time.astimezone(UTC)

    # Test naive datetime rejection
    with pytest.raises(ValueError, match="created_at must be timezone-aware"):
        BaseModel(created_at=datetime.now())


def test_base_model_update_tracking():
    """Test that updates are tracked properly.

    Update tracking should:
    1. Update the updated_at timestamp
    2. Leave created_at unchanged
    3. Store all timestamps in UTC
    4. Handle timezone conversions correctly
    """
    # Create model with time in different timezone
    ny_time = datetime.now(ZoneInfo("America/New_York"))
    model = BaseModel(created_at=ny_time)
    original_id = model.id
    original_created = model.created_at
    original_updated = model.updated_at

    # Wait a moment to ensure timestamp difference
    import time
    time.sleep(0.001)

    # Trigger update
    model.touch()

    # Verify changes
    assert model.id == original_id  # ID should never change
    assert model.created_at == original_created  # created_at should never change
    assert model.updated_at != original_updated  # updated_at should change
    assert model.updated_at > original_updated  # New timestamp should be later
    assert model.updated_at.tzinfo == UTC  # Still in UTC


def test_base_model_timezone_handling():
    """Test timezone handling across different timezones.

    The model should:
    1. Store all times in UTC regardless of input timezone
    2. Preserve the exact point in time during conversions
    3. Handle DST transitions correctly
    4. Accept any valid timezone
    """
    # Test different input timezones
    ny_time = datetime.now(ZoneInfo("America/New_York"))
    tokyo_time = datetime.now(ZoneInfo("Asia/Tokyo"))
    utc_time = datetime.now(timezone.utc)

    model_ny = BaseModel(created_at=ny_time)
    model_tokyo = BaseModel(created_at=tokyo_time)
    model_utc = BaseModel(created_at=utc_time)

    # All should be stored in UTC
    assert model_ny.created_at.tzinfo == UTC
    assert model_tokyo.created_at.tzinfo == UTC
    assert model_utc.created_at.tzinfo == UTC

    # All should represent the same points in time as inputs
    assert model_ny.created_at == ny_time.astimezone(UTC)
    assert model_tokyo.created_at == tokyo_time.astimezone(UTC)
    assert model_utc.created_at == utc_time

    # Test DST handling
    dst_time = datetime(2024, 7, 1, 12, 0, tzinfo=ZoneInfo("America/New_York"))
    non_dst_time = datetime(2024, 1, 1, 12, 0, tzinfo=ZoneInfo("America/New_York"))

    model_dst = BaseModel(created_at=dst_time)
    model_non_dst = BaseModel(created_at=non_dst_time)

    # Verify correct UTC offset differences
    assert dst_time.utcoffset() != non_dst_time.utcoffset()
    assert model_dst.created_at == dst_time.astimezone(UTC)
    assert model_non_dst.created_at == non_dst_time.astimezone(UTC)
