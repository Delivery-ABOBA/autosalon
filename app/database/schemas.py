from fastapi import UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional


class UserData(BaseModel):
    login: str
    password: str
    username: Optional[str] = None


class AlbumData(BaseModel):
    name: Optional[str] = None
    artist: Optional[int] = None
    image: UploadFile
    description: Optional[str] = None

    @classmethod
    def form(cls, name: Optional[str] = None, description: Optional[str] = None, artist: Optional[str] = None,
             image: UploadFile = File(...)):
        return cls(name=name, artist=artist, description=description, image=image)


class SongData(BaseModel):
    album: int
    name: str
    duration: Optional[int] = None
    file: UploadFile
    image: UploadFile
    artist: Optional[int] = None

    @classmethod
    def form(cls, name: str, album: int, artist: Optional[int] = None,
             duration: Optional[int] = None, image: UploadFile = File(...), file: UploadFile = File(...)):
        return cls(name=name, album=album, description=duration, image=image, file=file, artist=artist)


class CreateAlbum(BaseModel):
    file: UploadFile
    name: int


