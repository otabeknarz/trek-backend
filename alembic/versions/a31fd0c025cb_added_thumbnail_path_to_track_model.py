"""added thumbnail_path to Track model

Revision ID: a31fd0c025cb
Revises: 10229cd657bf
Create Date: 2024-11-05 02:24:53.582232

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a31fd0c025cb"
down_revision: Union[str, None] = "10229cd657bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_albums_id", table_name="albums")
    op.drop_table("albums")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_tracks_id", table_name="tracks")
    op.drop_table("tracks")
    op.drop_index("ix_user_tracks_id", table_name="user_tracks")
    op.drop_table("user_tracks")
    op.drop_index("ix_artists_id", table_name="artists")
    op.drop_table("artists")
    op.drop_table("track_artist")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "track_artist",
        sa.Column("track_id", sa.INTEGER(), nullable=False),
        sa.Column("artist_id", sa.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(
            ["artist_id"],
            ["artists.id"],
        ),
        sa.ForeignKeyConstraint(
            ["track_id"],
            ["tracks.id"],
        ),
        sa.PrimaryKeyConstraint("track_id", "artist_id"),
    )
    op.create_table(
        "artists",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("name", sa.VARCHAR(), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=True),
        sa.Column("created_at", sa.DATETIME(), nullable=True),
        sa.Column("is_active", sa.BOOLEAN(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_artists_id", "artists", ["id"], unique=1)
    op.create_table(
        "user_tracks",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("user_id", sa.INTEGER(), nullable=False),
        sa.Column("track_id", sa.INTEGER(), nullable=False),
        sa.Column("listen_count", sa.INTEGER(), nullable=True),
        sa.Column("last_listened", sa.DATETIME(), nullable=True),
        sa.Column("updated_at", sa.DATETIME(), nullable=True),
        sa.Column("created_at", sa.DATETIME(), nullable=True),
        sa.Column("is_active", sa.BOOLEAN(), nullable=True),
        sa.ForeignKeyConstraint(
            ["track_id"],
            ["tracks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_tracks_id", "user_tracks", ["id"], unique=False)
    op.create_table(
        "tracks",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("name", sa.VARCHAR(), nullable=False),
        sa.Column("duration", sa.INTEGER(), nullable=True),
        sa.Column("file_path", sa.VARCHAR(), nullable=False),
        sa.Column("album_id", sa.INTEGER(), nullable=True),
        sa.Column("updated_at", sa.DATETIME(), nullable=True),
        sa.Column("created_at", sa.DATETIME(), nullable=True),
        sa.Column("is_active", sa.BOOLEAN(), nullable=True),
        sa.ForeignKeyConstraint(
            ["album_id"],
            ["albums.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tracks_id", "tracks", ["id"], unique=1)
    op.create_table(
        "users",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("username", sa.VARCHAR(length=50), nullable=False),
        sa.Column("phone_number", sa.VARCHAR(length=15), nullable=True),
        sa.Column("password", sa.VARCHAR(length=255), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=True),
        sa.Column("created_at", sa.DATETIME(), nullable=True),
        sa.Column("is_active", sa.BOOLEAN(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone_number"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_id", "users", ["id"], unique=1)
    op.create_table(
        "albums",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("name", sa.VARCHAR(), nullable=False),
        sa.Column("release_year", sa.INTEGER(), nullable=True),
        sa.Column("updated_at", sa.DATETIME(), nullable=True),
        sa.Column("created_at", sa.DATETIME(), nullable=True),
        sa.Column("is_active", sa.BOOLEAN(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_albums_id", "albums", ["id"], unique=1)
    # ### end Alembic commands ###