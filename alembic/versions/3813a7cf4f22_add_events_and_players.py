"""add events and players

Revision ID: 3813a7cf4f22
Revises: None
Create Date: 2016-11-24 13:23:32.559478

"""

# revision identifiers, used by Alembic.
revision = '3813a7cf4f22'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('players',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=56), nullable=True),
    sa.Column('gender', sa.String(length=25), nullable=True),
    sa.Column('position', sa.String(length=25), nullable=True),
    sa.Column('od', sa.String(length=25), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('date', sa.String(length=55), nullable=True),
    sa.Column('tournament', sa.String(length=55), nullable=True),
    sa.Column('opponent', sa.String(length=55), nullable=True),
    sa.Column('seconds_elapsed', sa.Integer(), nullable=True),
    sa.Column('line', sa.String(length=25), nullable=True),
    sa.Column('our_score', sa.Integer(), nullable=True),
    sa.Column('their_score', sa.Integer(), nullable=True),
    sa.Column('event_type', sa.String(length=25), nullable=True),
    sa.Column('action', sa.String(length=25), nullable=True),
    sa.Column('passer', sa.Integer(), nullable=True),
    sa.Column('receiver', sa.Integer(), nullable=True),
    sa.Column('defender', sa.Integer(), nullable=True),
    sa.Column('player_1', sa.Integer(), nullable=True),
    sa.Column('player_2', sa.Integer(), nullable=True),
    sa.Column('player_3', sa.Integer(), nullable=True),
    sa.Column('player_4', sa.Integer(), nullable=True),
    sa.Column('player_5', sa.Integer(), nullable=True),
    sa.Column('player_6', sa.Integer(), nullable=True),
    sa.Column('player_7', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['player_1'], ['players.id'], ),
    sa.ForeignKeyConstraint(['player_2'], ['players.id'], ),
    sa.ForeignKeyConstraint(['player_3'], ['players.id'], ),
    sa.ForeignKeyConstraint(['player_4'], ['players.id'], ),
    sa.ForeignKeyConstraint(['player_5'], ['players.id'], ),
    sa.ForeignKeyConstraint(['player_6'], ['players.id'], ),
    sa.ForeignKeyConstraint(['player_7'], ['players.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('events')
    op.drop_table('players')
    ### end Alembic commands ###
