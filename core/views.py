from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from trek.database import get_db
from users.models import User
from .models import Track, Artist
from .schemas import (
    TrackCreateSchema,
    ArtistCreateSchema,
    TrackDeleteSchema,
    ListenToTrackSchema,
)

router = APIRouter()


@router.get("/trending-tracks/")
async def get_trending_tracks(
    days: int | None = 7, limit: int | None = 10, db: Session = Depends(get_db)
):
    # [(<Track()>, total_listens: int), ...]
    trending_tracks = Track.get_top_trending_tracks(db, days, limit)
    serialized_tracks = [
        {
            "id": track[0].id,
            "name": track[0].name,
            "duration": track[0].duration,
            "file_path": track[0].file_path,
            "total_listens": track[1],
        }
        for track in trending_tracks
    ]
    return {"trending_tracks": serialized_tracks}


@router.get("/tracks/")
async def get_tracks(db: Session = Depends(get_db)):
    tracks = Track.all(db)
    return {"tracks": tracks}


@router.post("/track/")
async def create_track(track_data: TrackCreateSchema, db: Session = Depends(get_db)):
    # Create the new Track instance
    new_track = Track(
        name=track_data.name,
        duration=track_data.duration,
        file_path=track_data.file_path,
        album_id=track_data.album_id,
    )

    # Save the track to the database using the inherited save method
    try:
        new_track.save(db)
    except Exception:
        raise HTTPException(
            status_code=500, detail="Failed to create track"
        )  # Handle any exceptions

    if not track_data.album_id:
        return {"message": "Track created successfully", "track_id": new_track.id}

    # Add artists to the track
    try:
        new_track.add_artists(db, track_data.artists_id)  # Associate artists
        db.commit()  # Commit after adding artists
    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(ve))  # Handle artist not found
    except Exception:
        db.rollback()  # Rollback on error
        raise HTTPException(
            status_code=500, detail="Failed to associate artists with track"
        )

    return {"message": "Track created successfully", "track_id": new_track.id}


@router.delete("/track/")
async def delete_track(track_data: TrackDeleteSchema, db: Session = Depends(get_db)):
    track = Track.get(db, id=track_data.id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    try:
        track.delete(db)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to delete track")

    return {"message": "Track deleted successfully"}


@router.get("/artists/")
async def get_artists(db: Session = Depends(get_db)):
    artists = Artist.all(db)
    return {"artists": artists}


@router.post("/artist/")
async def create_artist(artist_data: ArtistCreateSchema, db: Session = Depends(get_db)):
    new_artist = Artist(name=artist_data.name)
    new_artist.save(db)
    return {"message": "Artist created successfully", "artist_id": new_artist.id}


@router.delete("/artist/")
async def delete_artist(artist_data: ArtistCreateSchema, db: Session = Depends(get_db)):
    artist = Artist.get(db, name=artist_data.name)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    try:
        artist.delete(db)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to delete artist")

    return {"message": "Artist deleted successfully"}


@router.post("/listen/")
async def listen_to_track(
    credentials: ListenToTrackSchema, db: Session = Depends(get_db)
):
    user = User.get(db, id=credentials.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    track = Track.get(db, id=credentials.track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    user.listen_to_track(db, credentials.track_id)
    return {"message": "Track listened successfully"}
