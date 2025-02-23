"""Centralized definition of all tag association tables.

This module provides a single source of truth for all tag relationship tables,
preventing duplicate definitions and ensuring consistent behavior.
"""

from sqlalchemy import Table, Column, ForeignKey, Index
from .base_orm import BaseORMModel, GUID

# Contact-Tag association table
contact_tags = Table(
    'contact_tags',
    BaseORMModel.metadata,
    Column('entity_id', GUID, ForeignKey('contacts.id'), primary_key=True),
    Column('tag_id', GUID, ForeignKey('tags.id'), primary_key=True),
    Index('ix_contact_tags_tag_id', 'tag_id'),
    Index('ix_contact_tags_entity_id', 'entity_id')
)

# Note-Tag association table
note_tags = Table(
    'note_tags',
    BaseORMModel.metadata,
    Column('entity_id', GUID, ForeignKey('notes.id'), primary_key=True),
    Column('tag_id', GUID, ForeignKey('tags.id'), primary_key=True),
    Index('ix_note_tags_tag_id', 'tag_id'),
    Index('ix_note_tags_entity_id', 'entity_id')
)

# Statement-Tag association table
statement_tags = Table(
    'statement_tags',
    BaseORMModel.metadata,
    Column('entity_id', GUID, ForeignKey('statements.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', GUID, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    Index('ix_statement_tags_tag_id', 'tag_id'),
    Index('ix_statement_tags_entity_id', 'entity_id')
)
