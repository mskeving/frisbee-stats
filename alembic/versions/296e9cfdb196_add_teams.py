"""add teams

Revision ID: 296e9cfdb196
Revises: 3813a7cf4f22
Create Date: 2016-12-02 22:16:32.779041

"""

# revision identifiers, used by Alembic.
revision = '296e9cfdb196'
down_revision = '3813a7cf4f22'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('teams',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=56), nullable=True),
    sa.Column('region', sa.String(length=56), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'players', sa.Column('team_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'players', 'teams', ['team_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'players', type_='foreignkey')
    op.drop_column(u'players', 'team_id')
    op.drop_table('teams')
    ### end Alembic commands ###
