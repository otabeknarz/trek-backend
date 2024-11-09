from datetime import datetime

from argon2 import PasswordHasher
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Table,
    func,
)
from sqlalchemy.orm import Session, relationship

from core.models import Track, BaseModel
from .utils import get_number_id

ph = PasswordHasher()


class UserTrack(BaseModel):
    __tablename__ = "user_tracks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    listen_count = Column(Integer, default=0)  # Counts listens for each track
    last_listened = Column(
        DateTime, default=datetime.now
    )  # Timestamp of the last listen

    # Relationships to User and Track
    user = relationship("User", back_populates="tracks")
    track = relationship("Track", back_populates="users")

    def listen(self, db: Session):
        """Increment listen count and update last listened time."""
        self.listen_count += 1
        self.last_listened = datetime.now()
        db.commit()


class User(BaseModel):
    __tablename__ = "users"

    id = Column(
        Integer, primary_key=True, index=True, default=get_number_id, unique=True
    )
    username = Column(String(50), unique=True, nullable=False)
    phone_number = Column(String(15), unique=True, nullable=True)
    password = Column(String(255), nullable=False)
    tracks = relationship("UserTrack", back_populates="user")

    def __repr__(self):
        return (
            f"<User(id={self.id}, username='{self.username}', "
            f"phone_number='{self.phone_number}'>"
        )

    def set_password(self, raw_password):
        """Set the hashed password."""
        self.password = ph.hash(raw_password)

    def check_password(self, raw_password):
        """Check if the provided password matches the stored hash."""
        try:
            return ph.verify(self.password, raw_password)
        except Exception as e:
            # Consider logging the error here
            return False

    def listen_to_track(self, db: Session, track_id: int):
        """Record a listen event for the specified track."""
        # Check if there's an existing UserTrack entry for this user and track
        user_track = (
            db.query(UserTrack)
            .filter(UserTrack.user_id == self.id, UserTrack.track_id == track_id)
            .first()
        )

        if user_track:
            # If exists, increment listen count and update timestamp
            user_track.listen(db)
        else:
            # If not exists, create a new UserTrack entry
            new_user_track = UserTrack(
                user_id=self.id,
                track_id=track_id,
                listen_count=1,
                last_listened=datetime.utcnow(),
            )
            db.add(new_user_track)
            db.commit()

    def get_suggested_tracks(self, db: Session, limit: int = 10):
        """Suggest tracks to the user based on their listening history."""
        # Get top tracks the user has already listened to
        user_tracks = (
            db.query(UserTrack.track_id)
            .filter(UserTrack.user_id == self.id)
            .order_by(UserTrack.listen_count.desc())
            .limit(limit)
            .subquery()
        )

        # Recommend tracks similar to the ones the user has listened to
        recommendations = (
            db.query(Track)
            .filter(
                ~Track.id.in_(user_tracks)
            )  # Exclude tracks the user has already listened to
            .order_by(func.random())  # Randomize to simulate suggestions
            .limit(limit)
            .all()
        )
        return recommendations

    def get_listening_history(self, db: Session):
        """Retrieve the user's listening history."""
        user_tracks = db.query(UserTrack).filter(UserTrack.user_id == self.id).all()
        return [
            {
                "track_id": user_track.track_id,
                "listen_count": user_track.listen_count,
                "last_listened": user_track.last_listened,
                "track_details": {
                    "name": user_track.track.name,
                    "artist": user_track.track.artists[
                        0
                    ].name,  # Assuming the first artist for simplicity
                    "album": user_track.track.album.name,
                },
            }
            for user_track in user_tracks
        ]
