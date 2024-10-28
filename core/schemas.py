from pydantic import BaseModel


class TrackCreateSchema(BaseModel):
    name: str
    duration: int
    file_path: str
    artists_id: list[int]
    album_id: int | None = None


class TrackDeleteSchema(BaseModel):
    id: int


class ArtistCreateSchema(BaseModel):
    name: str


class AlbumCreateSchema(BaseModel):
    name: str
    release_year: int


class ListenToTrackSchema(BaseModel):
    user_id: int
    track_id: int
