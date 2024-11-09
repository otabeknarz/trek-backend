from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from trek.database import get_db
from users.models import User
from .models import Track, Artist, Album
from .schemas import (
    TrackCreateSchema,
    ArtistCreateSchema,
    TrackDeleteSchema,
    ListenToTrackSchema,
    TrackResponseSchema,
    ArtistResponseSchema,
    AlbumCreateSchema,
    AlbumResponseSchema,
    TrackUpdateSchema,
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


@router.get("/tracks/", response_model=list[TrackResponseSchema])
async def get_tracks(db: Session = Depends(get_db)) -> [Track]:
    tracks = Track.all(db)
    return tracks


@router.post("/track/", status_code=201, response_model=TrackResponseSchema)
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Handle any exceptions

    if not track_data.artists_id:
        return new_track

    # Add artists to the track
    try:
        new_track.add_artists(db, track_data.artists_id)  # Associate artists
        db.commit()  # Commit after adding artists
    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(ve))  # Handle artist not found
    except Exception as e:
        db.rollback()  # Rollback on error
        raise HTTPException(status_code=500, detail=str(e))

    return new_track


@router.patch("/track/{track_id}/", response_model=TrackResponseSchema)
async def update_track(
    track_id: int, track_data: TrackUpdateSchema, db: Session = Depends(get_db)
) -> Track:
    track = Track.get(db, id=track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    try:
        for key, value in track_data.dict(exclude_unset=True).items():
            setattr(track, key, value)
        track.save(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return track


@router.delete("/track/")
async def delete_track(track_data: TrackDeleteSchema, db: Session = Depends(get_db)):
    track = Track.get(db, id=track_data.id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    try:
        track.delete(db)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to delete track")

    return {"message": f"Track '{track.name}' deleted successfully"}


@router.get("/artists/", response_model=list[ArtistResponseSchema])
async def get_artists(db: Session = Depends(get_db)) -> [Artist]:
    artists = Artist.all(db)
    return artists


@router.post("/artist/", status_code=201, response_model=ArtistResponseSchema)
async def create_artist(
    artist_data: ArtistCreateSchema, db: Session = Depends(get_db)
) -> Artist:
    try:
        new_artist = Artist(name=artist_data.name)
        new_artist.save(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return new_artist


@router.delete("/artist/")
async def delete_artist(artist_data: ArtistCreateSchema, db: Session = Depends(get_db)):
    artist = Artist.get(db, name=artist_data.name)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    try:
        artist.delete(db)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to delete artist")

    return {"message": f"Artist '{artist.name}' deleted successfully"}


@router.get("/artist/{artist_id}/tracks/", response_model=list[TrackResponseSchema])
async def get_artist_tracks(artist_id: int, db: Session = Depends(get_db)) -> [Track]:
    artist = Artist.get(db, id=artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    return artist.tracks


@router.get("/albums/", response_model=list[AlbumResponseSchema])
async def get_albums(db: Session = Depends(get_db)) -> [Album]:
    albums = Album.all(db)
    return albums


@router.post("/albums/", status_code=201, response_model=AlbumCreateSchema)
async def create_album(
    album_data: AlbumCreateSchema, db: Session = Depends(get_db)
) -> Album:
    new_album = Album(name=album_data.name, release_year=album_data.release_year)
    new_album.save(db)
    return new_album


@router.post("/listen/", status_code=201)
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
