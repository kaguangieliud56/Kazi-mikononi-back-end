"""add conversations safely

Revision ID: e40ed808c6a4
Revises: adc54d264c94
Create Date: 2026-05-21 14:56:55.720614
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'e40ed808c6a4'
down_revision = 'adc54d264c94'
branch_labels = None
depends_on = None


def upgrade():
    # =========================
    # 1. CREATE CONVERSATIONS
    # =========================
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user1_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('user2_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    # =========================
    # 2. ADD COLUMN AS NULLABLE FIRST (IMPORTANT FIX)
    # =========================
    with op.batch_alter_table('messages') as batch_op:
        batch_op.add_column(sa.Column('conversation_id', sa.Integer(), nullable=True))

    # =========================
    # 3. CREATE FK AFTER COLUMN EXISTS
    # =========================
    with op.batch_alter_table('messages') as batch_op:
        batch_op.create_foreign_key(
            'fk_messages_conversation',
            'conversations',
            ['conversation_id'],
            ['id']
        )

    # =========================
    # 4. (OPTIONAL) BACKFILL OLD DATA
    # =========================
    # You can later run a script to populate conversations for old messages
    # before making this column NOT NULL


def downgrade():
    with op.batch_alter_table('messages') as batch_op:
        batch_op.drop_constraint('fk_messages_conversation', type_='foreignkey')
        batch_op.drop_column('conversation_id')

    op.drop_table('conversations')