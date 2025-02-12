"""Add entity_type to hashtags

Revision ID: 002
Create Date: 2024-03-19
"""
from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    # Add entity_type column
    op.add_column(
        'hashtags',
        sa.Column('entity_type', sa.String(), nullable=True)
    )

    # Update existing hashtags to be contact type
    conn = op.get_bind()
    conn.execute("""
        UPDATE hashtags
        SET entity_type = 'contact'
        WHERE entity_type IS NULL
    """)

    # Make entity_type not nullable
    op.alter_column(
        'hashtags',
        'entity_type',
        existing_type=sa.String(),
        nullable=False
    )

    # Drop old unique constraint on name
    op.drop_constraint('uq_hashtag_name', 'hashtags', type_='unique')

    # Add new unique constraint on name and entity_type
    op.create_unique_constraint(
        'uq_hashtag_name_type',
        'hashtags',
        ['name', 'entity_type']
    )


def downgrade() -> None:
    # Drop new unique constraint
    op.drop_constraint('uq_hashtag_name_type', 'hashtags', type_='unique')

    # Add back old unique constraint on name only
    op.create_unique_constraint('uq_hashtag_name', 'hashtags', ['name'])

    # Drop entity_type column
    op.drop_column('hashtags', 'entity_type')
