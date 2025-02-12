"""Add hashtag tables

Revision ID: 001
Create Date: 2024-03-19
"""
from typing import Sequence
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import JSON
from backend.app.models.base import GUID
import uuid

def upgrade() -> None:
    # Create hashtags table
    op.create_table(
        'hashtags',
        sa.Column('id', GUID, primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(), nullable=False),
        sa.UniqueConstraint('name')
    )

    # Create association table
    op.create_table(
        'contact_hashtags',
        sa.Column(
            'contact_id',
            GUID,
            sa.ForeignKey('contacts.id'),
            primary_key=True
        ),
        sa.Column(
            'hashtag_id',
            GUID,
            sa.ForeignKey('hashtags.id'),
            primary_key=True
        )
    )

    # Create temporary table for contacts
    op.create_table(
        'contacts_new',
        sa.Column('id', GUID, primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('contact_briefing_text', sa.String(), nullable=True),
        sa.Column('last_contact', sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            'sub_information',
            JSON,
            nullable=False,
            server_default='{}'
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False
        )
    )

    # Copy data from old contacts table
    op.execute("""
        INSERT INTO contacts_new (
            id, name, first_name, contact_briefing_text, last_contact,
            sub_information, created_at, updated_at
        )
        SELECT id, _name, _first_name, _contact_briefing_text, _last_contact,
               _sub_information, created_at, updated_at
        FROM contacts
    """)

    # Migrate hashtags data
    conn = op.get_bind()

    # Get existing contacts with hashtags
    contacts = conn.execute("""
        SELECT id, _hashtags
        FROM contacts
        WHERE _hashtags IS NOT NULL AND json_array_length(_hashtags) > 0
    """).fetchall()

    # Create hashtags and associations
    for contact_id, hashtags in contacts:
        for tag in hashtags:
            # Insert hashtag if it doesn't exist
            conn.execute(
                "INSERT OR IGNORE INTO hashtags (id, name) VALUES (?, ?)",
                [str(uuid.uuid4()), tag.lower()]
            )

            # Get hashtag id
            hashtag_id = conn.execute(
                "SELECT id FROM hashtags WHERE name = ?",
                [tag.lower()]
            ).scalar()

            # Create association
            conn.execute(
                "INSERT INTO contact_hashtags (contact_id, hashtag_id) VALUES (?, ?)",
                [str(contact_id), str(hashtag_id)]
            )

    # Drop old contacts table
    op.drop_table('contacts')

    # Rename new contacts table
    op.rename_table('contacts_new', 'contacts')

def downgrade() -> None:
    # Create temporary table for contacts with old schema
    op.create_table(
        'contacts_old',
        sa.Column('id', GUID, primary_key=True, default=uuid.uuid4),
        sa.Column('_name', sa.String(), nullable=False),
        sa.Column('_first_name', sa.String(), nullable=True),
        sa.Column('_contact_briefing_text', sa.String(), nullable=True),
        sa.Column('_last_contact', sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            '_sub_information',
            JSON,
            nullable=False,
            server_default='{}'
        ),
        sa.Column(
            '_hashtags',
            JSON,
            nullable=False,
            server_default='[]'
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False
        )
    )

    # Copy basic data back
    op.execute("""
        INSERT INTO contacts_old (
            id, _name, _first_name, _contact_briefing_text, _last_contact,
            _sub_information, created_at, updated_at
        )
        SELECT id, name, first_name, contact_briefing_text, last_contact,
               sub_information, created_at, updated_at
        FROM contacts
    """)

    # Migrate hashtags back to JSON array
    conn = op.get_bind()
    contacts = conn.execute("""
        SELECT c.id, json_group_array(h.name)
        FROM contacts c
        JOIN contact_hashtags ch ON c.id = ch.contact_id
        JOIN hashtags h ON ch.hashtag_id = h.id
        GROUP BY c.id
    """).fetchall()

    for contact_id, hashtags in contacts:
        conn.execute(
            "UPDATE contacts_old SET _hashtags = ? WHERE id = ?",
            [hashtags, str(contact_id)]
        )

    # Drop new tables
    op.drop_table('contact_hashtags')
    op.drop_table('hashtags')
    op.drop_table('contacts')

    # Rename old table back
    op.rename_table('contacts_old', 'contacts')
