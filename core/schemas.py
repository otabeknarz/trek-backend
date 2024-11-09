from datetime import datetime

from pydantic import BaseModel


class TrackCreateSchema(BaseModel):
    name: str
    duration: int
    file_path: str
    thumbnail_path: str
    artists_id: list[int]
    album_id: int | None = None


class TrackUpdateSchema(BaseModel):
    name: str | None = None
    duration: int | None = None
    file_path: str | None = None
    thumbnail_path: str | None = None
    artists_id: list[int] | None = None
    album_id: int | None = None


class TrackDeleteSchema(BaseModel):
    id: int


class ArtistCreateSchema(BaseModel):
    name: str


class ArtistResponseSchema(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    is_active: bool


class AlbumCreateSchema(BaseModel):
    name: str
    release_year: int


class AlbumResponseSchema(BaseModel):
    id: int
    name: str
    release_year: int
    created_at: datetime
    updated_at: datetime
    is_active: bool


class ListenToTrackSchema(BaseModel):
    user_id: int
    track_id: int


class TrackResponseSchema(BaseModel):
    id: int
    name: str
    duration: int
    file_path: str
    thumbnail_path: str | None
    album: AlbumResponseSchema | None
    artists: list[ArtistResponseSchema]
    created_at: datetime
    updated_at: datetime
    is_active: bool
