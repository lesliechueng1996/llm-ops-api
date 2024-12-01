"""empty message

Revision ID: 0806f580d7b5
Revises: 
Create Date: 2024-12-02 03:26:08.772035

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0806f580d7b5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('app',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('account_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('icon', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_app_id')
    )
    with op.batch_alter_table('app', schema=None) as batch_op:
        batch_op.create_index('idx_app_account_id', ['account_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('app', schema=None) as batch_op:
        batch_op.drop_index('idx_app_account_id')

    op.drop_table('app')
    # ### end Alembic commands ###
