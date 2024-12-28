"""empty message

Revision ID: f313569a8d16
Revises: 643902daa51e
Create Date: 2024-12-28 21:01:41.689052

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f313569a8d16'
down_revision = '643902daa51e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('name', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=False),
    sa.Column('email', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=False),
    sa.Column('password', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=False),
    sa.Column('password_salt', sa.String(length=255), nullable=True),
    sa.Column('avatar', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=False),
    sa.Column('last_login_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.Column('last_login_ip', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_account_id')
    )
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.create_index('idx_account_email', ['email'], unique=False)

    op.create_table('account_oauth',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('account_id', sa.UUID(), nullable=False),
    sa.Column('provider', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=False),
    sa.Column('openid', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=False),
    sa.Column('encrypted_token', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_account_oauth_id')
    )
    with op.batch_alter_table('account_oauth', schema=None) as batch_op:
        batch_op.create_index('idx_account_oauth_account_id', ['account_id'], unique=False)
        batch_op.create_index('idx_account_oauth_provider', ['provider'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('account_oauth', schema=None) as batch_op:
        batch_op.drop_index('idx_account_oauth_provider')
        batch_op.drop_index('idx_account_oauth_account_id')

    op.drop_table('account_oauth')
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.drop_index('idx_account_email')

    op.drop_table('account')
    # ### end Alembic commands ###
