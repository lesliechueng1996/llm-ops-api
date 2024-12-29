"""empty message

Revision ID: ee50d8b87af2
Revises: f313569a8d16
Create Date: 2024-12-29 18:30:02.872029

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ee50d8b87af2'
down_revision = 'f313569a8d16'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('app_config',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('app_id', sa.UUID(), nullable=False),
    sa.Column('model_config', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('dialog_round', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('preset_prompt', sa.Text(), server_default=sa.text("''::text"), nullable=False),
    sa.Column('tools', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('workflows', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('retrieval_config', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('long_term_memory', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('opening_statement', sa.Text(), server_default=sa.text("''::text"), nullable=False),
    sa.Column('opening_questions', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('speech_to_text', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('text_to_speech', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('review_config', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_app_config_id')
    )
    with op.batch_alter_table('app_config', schema=None) as batch_op:
        batch_op.create_index('idx_app_config_app_id', ['app_id'], unique=False)

    op.create_table('app_config_version',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('app_id', sa.UUID(), nullable=False),
    sa.Column('model_config', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('dialog_round', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('preset_prompt', sa.Text(), server_default=sa.text("''::text"), nullable=False),
    sa.Column('tools', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('workflows', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('datasets', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('retrieval_config', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('long_term_memory', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('opening_statement', sa.Text(), server_default=sa.text("''::text"), nullable=False),
    sa.Column('opening_questions', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('speech_to_text', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('text_to_speech', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('review_config', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('version', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('config_type', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_app_config_version_id')
    )
    with op.batch_alter_table('app_config_version', schema=None) as batch_op:
        batch_op.create_index('idx_app_config_version_app_id', ['app_id'], unique=False)

    with op.batch_alter_table('app', schema=None) as batch_op:
        batch_op.add_column(sa.Column('app_config_id', sa.UUID(), nullable=True))
        batch_op.add_column(sa.Column('draft_app_config_id', sa.UUID(), nullable=True))
        batch_op.add_column(sa.Column('debug_conversation_id', sa.UUID(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('app', schema=None) as batch_op:
        batch_op.drop_column('debug_conversation_id')
        batch_op.drop_column('draft_app_config_id')
        batch_op.drop_column('app_config_id')

    with op.batch_alter_table('app_config_version', schema=None) as batch_op:
        batch_op.drop_index('idx_app_config_version_app_id')

    op.drop_table('app_config_version')
    with op.batch_alter_table('app_config', schema=None) as batch_op:
        batch_op.drop_index('idx_app_config_app_id')

    op.drop_table('app_config')
    # ### end Alembic commands ###
