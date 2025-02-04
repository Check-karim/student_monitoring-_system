"""empty message

Revision ID: f3110098387b
Revises: 2e4ada8ff0e8
Create Date: 2024-08-04 09:52:31.281575

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3110098387b'
down_revision = '2e4ada8ff0e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('course',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('acronym', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('acronym')
    )
    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=255), nullable=False))
        batch_op.add_column(sa.Column('phone_number', sa.String(length=20), nullable=False))
        batch_op.add_column(sa.Column('course_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'course', ['course_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('course_id')
        batch_op.drop_column('phone_number')
        batch_op.drop_column('name')

    op.drop_table('course')
    # ### end Alembic commands ###
