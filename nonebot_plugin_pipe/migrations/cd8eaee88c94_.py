"""empty message

Revision ID: cd8eaee88c94
Revises: 
Create Date: 2023-02-26 23:52:40.933074

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "cd8eaee88c94"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "nonebot_plugin_pipe_message",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Uuid(), nullable=False),
        sa.Column("src", sa.String(), nullable=False),
        sa.Column("src_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("nonebot_plugin_pipe_message")
    # ### end Alembic commands ###
