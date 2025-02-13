"""Integration tests for SQLAlchemy tag repository."""
import pytest
from datetime import datetime, UTC, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from sqlalchemy import select, and_

from backend.app.models.tag import Tag, EntityType
from backend.app.repositories.sqlalchemy.tag_repository import SQLAlchemyTagRepository, TagORM


TEST_UUID = UUID("11111111-1111-1111-1111-111111111111")
TEST_UUID_2 = UUID("22222222-2222-2222-2222-222222222222")
TEST_DATETIME = datetime(2024, 1, 1, tzinfo=UTC)


@pytest.fixture
def tag_repository(db_session: Session) -> SQLAlchemyTagRepository:
    """Create a tag repository for testing.

    Args:
        db_session: SQLAlchemy session fixture

    Returns:
        SQLAlchemyTagRepository: Repository instance for testing
    """
    return SQLAlchemyTagRepository(db_session)


@pytest.fixture
def sample_tag() -> Tag:
    """Create a sample tag for testing.

    Returns:
        Tag: A test tag instance
    """
    return Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#test"
    )


def test_save_and_find_by_entity(
    tag_repository: SQLAlchemyTagRepository,
    sample_tag: Tag,
    db_session: Session
) -> None:
    """Test saving a tag and retrieving it by entity.

    Should:
    - Save a new tag successfully
    - Find the tag by entity ID and type
    - Return correct tag data
    """
    # Save the tag
    tag_repository.save(sample_tag)
    db_session.commit()

    # Find the tag by entity
    found = tag_repository.find_by_entity(TEST_UUID, EntityType.CONTACT)
    assert len(found) == 1
    found_tag = found[0]
    assert found_tag.entity_id == TEST_UUID
    assert found_tag.entity_type == EntityType.CONTACT
    assert found_tag.name == "#test"


def test_save_updates_existing_tag(
    tag_repository: SQLAlchemyTagRepository,
    sample_tag: Tag,
    db_session: Session
) -> None:
    """Test that saving a tag with same natural key updates the existing one.

    Should:
    - Save initial tag with frequency
    - Update existing tag with new frequency
    - Verify updated frequency is persisted
    """
    # Set initial frequency and save
    sample_tag.set_frequency(7)  # Weekly
    tag_repository.save(sample_tag)
    db_session.commit()

    # Create new tag with same natural key but different frequency
    updated_tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#test"
    )
    updated_tag.set_frequency(14)  # Biweekly
    tag_repository.save(updated_tag)
    db_session.commit()

    # Find tag - should be updated
    found = tag_repository.find_by_entity(TEST_UUID, EntityType.CONTACT)
    assert len(found) == 1
    found_tag = found[0]
    assert found_tag.frequency_days == 14


def test_find_by_name(
    tag_repository: SQLAlchemyTagRepository,
    db_session: Session
) -> None:
    """Test finding tags by name (case-insensitive).

    Should:
    - Find tags regardless of case
    - Return all matching tags
    - Preserve original tag names
    """
    # Create tags with same name, different entities
    tag1 = Tag(entity_id=TEST_UUID, entity_type=EntityType.CONTACT, name="#TEST")
    tag2 = Tag(entity_id=TEST_UUID_2, entity_type=EntityType.CONTACT, name="#test")
    tag_repository.save(tag1)
    tag_repository.save(tag2)
    db_session.commit()

    # Find by name should return both
    found = tag_repository.find_by_name("#test")
    assert len(found) == 2
    assert all(t.name.lower() == "#test" for t in found)
    assert {t.entity_id for t in found} == {TEST_UUID, TEST_UUID_2}


def test_find_stale(
    tag_repository: SQLAlchemyTagRepository,
    db_session: Session
) -> None:
    """Test finding stale tags.

    Should:
    - Correctly identify stale tags based on frequency
    - Not return fresh tags
    - Use consistent time for comparison
    """
    # Create fresh tag
    fresh_tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#fresh"
    )
    fresh_tag.set_frequency(7)  # Weekly
    fresh_tag.update_last_contact(TEST_DATETIME)
    tag_repository.save(fresh_tag)

    # Create stale tag
    stale_tag = Tag(
        entity_id=TEST_UUID_2,
        entity_type=EntityType.CONTACT,
        name="#stale"
    )
    stale_tag.set_frequency(7)  # Weekly
    stale_tag.update_last_contact(TEST_DATETIME - timedelta(days=8))
    tag_repository.save(stale_tag)

    db_session.commit()

    # Mock current time by patching the Tag.is_stale method
    def mock_now() -> datetime:
        return TEST_DATETIME

    original_now = Tag.get_current_time
    Tag.get_current_time = staticmethod(mock_now)  # type: ignore
    try:
        # Find stale tags
        stale = tag_repository.find_stale()
        assert len(stale) == 1
        assert stale[0].name == "#stale"
    finally:
        # Restore original method
        Tag.get_current_time = original_now  # type: ignore


def test_delete(
    tag_repository: SQLAlchemyTagRepository,
    sample_tag: Tag,
    db_session: Session,
    engine: Engine
) -> None:
    """Test deleting a tag.

    Should:
    - Successfully delete the tag
    - Verify deletion in current session
    - Verify deletion in new session
    """
    # Save the tag and get its ID
    saved_tag = tag_repository.save(sample_tag)
    db_session.commit()

    # Get the ORM instance to get the ID
    stmt = select(TagORM).where(and_(
        TagORM.entity_id == saved_tag.entity_id,
        TagORM.entity_type == saved_tag.entity_type.value,
        TagORM.name == saved_tag.name
    ))
    orm_tag = db_session.execute(stmt).scalar_one()
    tag_id = orm_tag.id

    # Delete the tag
    tag_repository.delete(saved_tag)
    db_session.commit()

    # Verify deletion in the same session first
    found = tag_repository.find_by_id(tag_id)
    assert found is None

    # Double-check with a new session
    new_session = Session(engine)
    new_repo = SQLAlchemyTagRepository(new_session)
    try:
        found = new_repo.find_by_id(tag_id)
        assert found is None
    finally:
        new_session.close()


def test_delete_nonexistent_tag(
    tag_repository: SQLAlchemyTagRepository,
    db_session: Session
) -> None:
    """Test deleting a tag that doesn't exist.

    Should:
    - Not raise any errors
    - Leave database in consistent state
    """
    # Clean up any existing tags
    db_session.query(TagORM).delete()
    db_session.commit()

    # Create a tag that was never saved
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#nonexistent"
    )

    # Try to delete a tag that was never saved
    tag_repository.delete(tag)
    db_session.commit()

    # Database should still work normally after
    tag_repository.save(tag)
    db_session.commit()

    found = tag_repository.find_by_entity(TEST_UUID, EntityType.CONTACT)
    assert len(found) == 1


def test_disable_tag_frequency(
    tag_repository: SQLAlchemyTagRepository,
    db_session: Session
) -> None:
    """Test disabling frequency tracking on a tag.

    Should:
    - Clear frequency when set to None
    - Clear last_contact when frequency is disabled
    - Persist these changes to database
    """
    # Clean up any existing tags
    db_session.query(TagORM).delete()
    db_session.commit()

    # Create a new tag with frequency
    tag = Tag(
        entity_id=TEST_UUID,
        entity_type=EntityType.CONTACT,
        name="#frequency_test"
    )
    tag.set_frequency(7)  # Weekly
    tag_repository.save(tag)
    db_session.commit()

    # Verify initial state
    found = tag_repository.find_by_entity(TEST_UUID, EntityType.CONTACT)
    assert len(found) == 1
    assert found[0].frequency_days == 7
    assert found[0].last_contact is not None

    # Disable frequency
    found[0].set_frequency(None)
    tag_repository.save(found[0])
    db_session.commit()

    # Verify frequency is disabled
    found = tag_repository.find_by_entity(TEST_UUID, EntityType.CONTACT)
    assert len(found) == 1
    assert found[0].frequency_days is None
    assert found[0].last_contact is None
