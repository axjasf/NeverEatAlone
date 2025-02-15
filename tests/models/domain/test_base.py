"""Tests for the Base domain model."""

from datetime import datetime, UTC
from uuid import UUID
from backend.app.models.domain.base_model import BaseModel


def test_base_model_initialization():
    """Test base model initialization.

    Base model should:
    1. Generate a UUID on creation
    2. Set created_at timestamp
    3. Set updated_at equal to created_at initially
    """
    model = BaseModel()

    assert isinstance(model.id, UUID)
    assert isinstance(model.created_at, datetime)
    assert isinstance(model.updated_at, datetime)
    assert model.created_at.tzinfo == UTC  # Ensure UTC timezone
    assert model.updated_at == model.created_at


def test_base_model_update_tracking():
    """Test that updates are tracked properly.

    Update tracking should:
    1. Update the updated_at timestamp
    2. Leave created_at unchanged
    """
    model = BaseModel()
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
