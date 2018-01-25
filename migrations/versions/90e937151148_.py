"""empty message

Revision ID: 90e937151148
Revises: 65239bc08fea
Create Date: 2018-01-25 12:42:18.126622

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90e937151148'
down_revision = '65239bc08fea'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_name', sa.String(length=50), nullable=False),
    sa.Column('event_cartegory', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_cartegory'], ['eventlists.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('category_name'),
    sa.UniqueConstraint('id')
    )
    op.drop_column('eventlists', 'category')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('eventlists', sa.Column('category', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.drop_table('event_category')
    # ### end Alembic commands ###
