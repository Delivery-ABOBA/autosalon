from uuid import uuid4

from bcrypt import checkpw, hashpw, gensalt
from fastapi import HTTPException
from mutagen.mp3 import MP3
from sqlalchemy import delete
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from app.database import models, schemas


url = "http://localhost"


# region auth
async def register(data: schemas.UserData, db: Session):
    db_data = db.query(models.Users).filter(models.Users.login == data.login).first()
    if db_data is None:
        try:
            max_id = db.query(func.max(models.Users.id)).scalar() + 1
        except TypeError:
            max_id = 1
        salt = gensalt()
        data = models.Users(id=max_id, login=data.login, password=hashpw(data.password.encode(), salt).decode(),
                            username=data.username)
        db.add(data)
        db.commit()
        db.refresh(data)
        return data
    else:
        return False


async def login(user_data: schemas.UserData, db: Session):
    db_data = db.query(models.Users).filter(models.Users.login == user_data.login).first()
    if db_data is None:
        return None
    else:
        if checkpw(user_data.password.encode('utf-8'), db_data.password.encode('utf-8')):
            return db_data
        else:
            return False


# endregion
# region user
async def set_image(image: bytes, user_id: int, name: str, db: Session):
    name = str(uuid4()) + name
    with open(f"app/storage/users/{name}", "wb") as file:
        file.write(image)
    try:
        max_id = db.query(func.max(models.Images.id)).scalar() + 1
    except TypeError:
        max_id = 1
    image = models.Images(id=max_id, type="users", name=name)
    db.add(image)
    db.commit()
    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    user.image = image.id
    db.commit()


# endregion
# region albums
async def get_random_album(db: Session):
    return db.query(models.Albums, models.Users, models.Images).select_from(models.Albums)\
        .join(models.Users).join(models.Images)\
        .order_by(func.random()).limit(10).all()


async def get_album_songs(id: int, db: Session):
    res = []
    result = db.query(models.Songs, models.Users).select_from(models.Songs)\
        .join(models.Albums, models.Songs.album == models.Albums.id)\
        .join(models.Users, models.Albums.artist == models.Users.id)\
        .filter(models.Songs.album == id).all()
    if result is None:
        raise HTTPException(status_code=404)
    for i in result:
        res.append({
            "mp3": url + "/songs/" + str(i.Songs.id),
            "poster": url + "/songs/image/" + str(i.Songs.image),
            "title": i.Songs.name,
            "duration": i.Songs.duration,
            "id": i.Songs.id,
            "artist": i.Users.username
        })
    return res


async def create_album(data: schemas.AlbumData, db: Session):
    name = str(uuid4()) + data.image.filename
    with open(f"app/storage/releases/{name}", "wb") as file:
        file.write(await data.image.read())
    try:
        img_id = db.query(func.max(models.Images.id)).scalar() + 1
    except TypeError:
        img_id = 1
    image = models.Images(id=img_id, type="releases", name=name)
    db.add(image)
    db.commit()
    try:
        max_id = db.query(func.max(models.Albums.id)).scalar() + 1
    except TypeError:
        max_id = 1
    album = models.Albums(id=max_id, name=data.name, artist=data.artist, description=data.description, image=img_id)
    db.add(album)
    db.commit()
    db.refresh(album)
    return album


async def add_track_to_album(data: schemas.SongData, db: Session):
    name = str(uuid4()) + data.image.filename
    with open(f"app/storage/releases/{name}", "wb") as file:
        file.write(await data.image.read())
    try:
        img_id = db.query(func.max(models.Images.id)).scalar() + 1
    except TypeError:
        img_id = 1
    image = models.Images(id=img_id, type="releases", name=name)
    db.add(image)
    db.commit()
    name = str(uuid4()) + data.file.filename
    with open(f"app/storage/tracks/{name}", "wb") as file:
        file.write(await data.file.read())
    try:
        max_id = db.query(func.max(models.Songs.id)).scalar() + 1
    except TypeError:
        max_id = 1
    audio = MP3(f"app/storage/tracks/{name}")
    duration = int(audio.info.length)
    duration_text = f"{int(duration / 60)}:{duration % 60}"
    song = models.Songs(id=max_id, name=data.name, album=data.album, image=img_id, file=name,
                        duration=duration_text)
    db.add(song)
    db.commit()
    db.refresh(song)
    return song



async def remove_track_from_album(song_id: int, artist: int, db: Session):
    db.execute(delete(models.Songs).where(models.Songs.id == song_id))
    db.commit()
    return True


async def remove_album(album_id: int, artist: int, db: Session):
    db.execute(delete(models.Songs).where(models.Songs.album == album_id))
    db.commit()
    db.execute(delete(models.Albums).where(models.Albums.id == album_id, models.Albums.artist == artist))
    db.commit()
    return True


# endregion
# region songs
async def get_song(id: int, db: Session):
    result = db.query(models.Songs).filter(models.Songs.id == id).first()
    if result is None:
        raise HTTPException(status_code=404)
    return result


async def get_file(id: int, db: Session):
    result = db.query(models.Images).filter(models.Images.id == id).first()
    if result is None:
        raise HTTPException(status_code=404)
    return result


async def get_random_songs(db: Session):
    result = db.query(models.Songs).order_by(func.random()).limit(10).all()
    if result is None or len(result) == 0:
        raise HTTPException(status_code=404)
    return result


async def search(type, name, db):
    if type == 1:
        result = db.query(models.Songs, models.Users).select_from(models.Songs).join(models.Albums)\
            .join(models.Users, models.Users.id == models.Albums.artist)\
            .where(models.Songs.name.like(f"%{name}%") )
    elif type == 2:
        result = db.query(models.Albums, models.Users).join(models.Users).where(models.Albums.name.like(f"%{name}%") )
    else:
        result = db.query(models.Users).select_from(models.Albums).join(models.Users)\
            .where(models.Users.username.like(f"%{name}%") )
    result = result.all()
    if result is None or len(result) == 0:
        raise HTTPException(status_code=404)
    return result


# endregion
# region playlists
async def get_my_data(id, db):
    result = db.query(models.Users).filter(models.Users.id == id).first()
    if result is None:
        raise HTTPException(status_code=404)
    result.image = url + "/songs/image/" + str(result.image)
    return result


async def get_playlist_songs(user_id: int, db: Session):
    res = []
    result = db.query(models.Songs, models.Users)\
        .join(models.PlaylistSongs, models.PlaylistSongs.song_id == models.Songs.id)\
        .join(models.Albums, models.Albums.id == models.Songs.album)\
        .join(models.Users, models.Albums.artist == models.Users.id)\
        .filter(models.PlaylistSongs.user_id == user_id).all()
    if result is None or len(result) == 0:
        raise HTTPException(status_code=404)
    for i in result:
        res.append({
            "mp3": url + "/songs/" + str(i.Songs.id),
            "poster": url + "/songs/image/" + str(i.Songs.image),
            "title": i.Songs.name,
            "duration": i.Songs.duration,
            "id": i.Songs.id,
            "artist": i.Users.username
        })
    return res


async def add_track_to_playlist(id: int, user_id: int, db: Session):
    playlist = models.PlaylistSongs(song_id=id, user_id=user_id)
    db.add(playlist)
    db.commit()
    return True


async def remove_track_from_playlist(id: int, user_id: int, db: Session):
    db.execute(delete(models.PlaylistSongs).where(models.PlaylistSongs.song_id == id,
                                                  models.PlaylistSongs.user_id == user_id))
    db.commit()
    return True


async def get_favorites_by_user(id: int, db: Session):
    result = db.query(models.Favorites, models.Users, models.Albums)\
        .outerjoin(models.Albums, models.Favorites.album_id == models.Albums.id)\
        .outerjoin(models.Users, models.Favorites.artist_id == models.Users.id)\
        .where(models.Favorites.user_id == id).all()
    if result is None or len(result) == 0:
        raise HTTPException(status_code=404)
    return result


async def add_artist_to_favs(id: int, user_id: int, db: Session):
    fav = models.Favorites(user_id=user_id, artist_id=id)
    db.add(fav)
    db.commit()
    return True


async def add_album_to_favs(id: int, user_id: int, db: Session):
    fav = models.Favorites(user_id=user_id, album_id=id)
    db.add(fav)
    db.commit()
    return True


async def remove_artist_to_favs(id: int, user_id: int, db: Session):
    db.execute(delete(models.Favorites).where(models.Favorites.user_id == user_id, models.Favorites.artist_id == id))
    db.commit()
    return True


async def remove_album_to_favs(id: int, user_id: int, db: Session):
    db.execute(delete(models.Favorites).where(models.Favorites.user_id == user_id, models.Favorites.album_id == id))
    db.commit()
    return True


# endregion
# region artists
async def get_random_artist(db: Session):
    result = db.query(models.Users).select_from(models.Albums).join(models.Users).order_by(func.random()).limit(10).all()
    if result is None or len(result) == 0:
        raise HTTPException(status_code=404)
    return result


async def get_artist_albums(id: int, user_id: int, db: Session):
    result = db.query(models.Albums, models.Images, models.Users).select_from(models.Albums)\
        .join(models.Images, models.Albums.image == models.Images.id)\
        .join(models.Users, models.Albums.artist == models.Users.id).filter(models.Albums.artist == id).all()
    if result is None or len(result) == 0:
        raise HTTPException(status_code=404)

    res = db.query(models.Favorites).where(models.Favorites.user_id == user_id,
                                              models.Favorites.artist_id == id).first()
    if res is None:
        is_sub = False
    else:
        is_sub = True
    return result, is_sub


# endregion
# region preset
def preset(db: Session):
    img1 = models.Images(id=1, type="posters", name="img.png")
    img2 = models.Images(id=2, type="posters", name="img_1.png")
    img3 = models.Images(id=3, type="posters", name="img_2.png")
    db.add(img1)
    db.add(img2)
    db.add(img3)
    img1 = models.Images(id=4, type="releases", name="img.png")
    img2 = models.Images(id=5, type="releases", name="img_1.png")
    img3 = models.Images(id=6, type="releases", name="img_2.png")
    db.add(img1)
    db.add(img2)
    db.add(img3)
    img1 = models.Images(id=7, type="users", name="img.png")
    img2 = models.Images(id=8, type="users", name="img_1.png")
    img3 = models.Images(id=9, type="users", name="img_2.png")
    db.add(img1)
    db.add(img2)
    db.add(img3)
    db.commit()
    salt = gensalt()
    art1 = models.Users(id=1, login="artist_1", password=hashpw("123456".encode(), salt).decode(), username="Artist 1",
                        image=7)
    art2 = models.Users(id=2, login="artist_2", password=hashpw("123456".encode(), salt).decode(), username="Artist 2",
                        image=8)
    art3 = models.Users(id=3, login="artist_3", password=hashpw("123456".encode(), salt).decode(), username="Artist 3",
                        image=9)
    db.add(art1)
    db.add(art2)
    db.add(art3)
    db.commit()
    alb1 = models.Albums(id=1, name="Album 1", artist=1, description="Album 1 description", image=4)
    alb2 = models.Albums(id=2, name="Album 2", artist=2, description="Album 2 description", image=5)
    alb3 = models.Albums(id=3, name="Album 3", artist=3, description="Album 3 description", image=6)
    db.add(alb1)
    db.add(alb2)
    db.add(alb3)
    db.commit()
    song1 = models.Songs(id=1, name="Song 1", album=1, duration="2.28", image=1, file="12071151.mp3")
    song2 = models.Songs(id=2, name="Song 2", album=1, duration="2.28", image=2, file="12071151.mp3")
    song3 = models.Songs(id=3, name="Song 3", album=1, duration="2.28", image=3, file="12071151.mp3")
    db.add(song1)
    db.add(song2)
    db.add(song3)
    db.commit()
    song1 = models.Songs(id=4, name="Song 1", album=2, duration="2.28", image=1, file="12071151.mp3")
    song2 = models.Songs(id=5, name="Song 2", album=2, duration="2.28", image=2, file="12071151.mp3")
    song3 = models.Songs(id=6, name="Song 3", album=2, duration="2.28", image=3, file="12071151.mp3")
    db.add(song1)
    db.add(song2)
    db.add(song3)
    db.commit()
    song1 = models.Songs(id=7, name="Song 1", album=3, duration="2.28", image=1, file="12071151.mp3")
    song2 = models.Songs(id=8, name="Song 2", album=3, duration="2.28", image=2, file="12071151.mp3")
    song3 = models.Songs(id=9, name="Song 3", album=3, duration="2.28", image=3, file="12071151.mp3")
    db.add(song1)
    db.add(song2)
    db.add(song3)
    db.commit()
    test_user = models.Users(id=4, login="admin", password=hashpw("123456".encode(), salt).decode(), username="Admin",
                             image=9)
    db.add(test_user)
    db.commit()


# endregion