from datetime import datetime, timedelta

from sqlalchemy import Column, String, Integer, ForeignKey, Table, func, DateTime
from sqlalchemy.orm import relationship, Session

from trek.database import Base
from users.utils import get_number_id


class BaseModel(Base):
    __abstract__ = True
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = Column(DateTime, default=datetime.now)

    def save(self, db: Session):
        """Save the model instance to the database."""
        try:
            db.add(self)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e  # Consider logging the error here

    def delete(self, db: Session):
        """Delete the model instance from the database."""
        try:
            db.delete(self)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e  # Consider logging the error here

    @classmethod
    def get(cls, db: Session, **kwargs):
        """Get a single model instance based on provided filters."""
        return db.query(cls).filter_by(**kwargs).first()

    @classmethod
    def filter(cls, db: Session, **kwargs):
        """Filter model instances based on provided filters."""
        return db.query(cls).filter_by(**kwargs).all()

    @classmethod
    def all(cls, db: Session):
        """Get all model instances."""
        return db.query(cls).all()


track_artist = Table(
    "track_artist",
    Base.metadata,
    Column("track_id", Integer, ForeignKey("tracks.id"), primary_key=True),
    Column("artist_id", Integer, ForeignKey("artists.id"), primary_key=True),
)


class Artist(BaseModel):
    __tablename__ = "artists"

    id = Column(
        Integer, primary_key=True, index=True, default=get_number_id, unique=True
    )
    name = Column(String, unique=True, nullable=False)

    # Many-to-many relationship with Track
    tracks = relationship("Track", secondary=track_artist, back_populates="artists")


class Album(BaseModel):
    __tablename__ = "albums"

    id = Column(
        Integer, primary_key=True, index=True, default=get_number_id, unique=True
    )
    name = Column(String, nullable=False)
    release_year = Column(Integer)

    # One-to-many relationship with Track
    tracks = relationship("Track", back_populates="album")


class Track(BaseModel):
    __tablename__ = "tracks"

    id = Column(
        Integer, primary_key=True, index=True, default=get_number_id, unique=True
    )
    name = Column(String, nullable=False)
    duration = Column(Integer)  # in seconds
    file_path = Column(String, nullable=False)  # Store file path or URL

    # Foreign key to Album
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=True)

    # Many-to-many relationship with Artist
    artists = relationship("Artist", secondary=track_artist, back_populates="tracks")

    # Relationship with Album
    album = relationship("Album", back_populates="tracks")

    users = relationship("UserTrack", back_populates="track")

    def add_artists(self, db: Session, artist_ids: list[int]):
        """Add artists to this track."""
        for artist_id in artist_ids:
            artist = Artist.get(db, id=artist_id)  # Use the get method from BaseModel
            if artist:
                self.artists.append(artist)  # Add artist to the track's artist list
            else:
                raise ValueError(f"Artist with ID {artist_id} not found")

    @classmethod
    def get_most_listened_tracks(cls, db: Session, limit: int = 10):
        from users.models import UserTrack

        """Returns the most listened tracks across all users."""
        return (
            db.query(cls, func.sum(UserTrack.listen_count).label("total_listens"))
            .join(UserTrack)
            .group_by(cls.id)
            .order_by(func.sum(UserTrack.listen_count).desc())
            .limit(limit)
            .all()
        )

    @classmethod
    def get_top_trending_tracks(cls, db: Session, days: int = 7, limit: int = 10):
        from users.models import UserTrack

        """Returns tracks that are trending based on recent listens."""
        recent_date = datetime.now() - timedelta(days=days)
        return (
            db.query(cls, func.sum(UserTrack.listen_count).label("recent_listens"))
            .join(UserTrack)
            .filter(UserTrack.last_listened >= recent_date)
            .group_by(cls.id)
            .order_by(func.sum(UserTrack.listen_count).desc())
            .limit(limit)
            .all()
        )
