from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.database import crud, schemas
from app.dependencies import get_db
from app.funcs.utils import get_jwt_sub
import requests
import json
from datetime import date
import os
from app.dependencies import get_settings

settings = get_settings()

router = APIRouter(prefix="/sport", tags=["Sport"])


@router.get("/")
async def get_sports(endpoint: str, sport: str, db: Session = Depends(get_db)):

    url = f"https://livescore6.p.rapidapi.com/{endpoint}/v2/list-by-date"

    querystring = {"Category":sport,"Date":f"{date.today()}","Timezone":"3"}
    
    headers = {
    	"X-RapidAPI-Key": "f04a55b9a6msh71c0ad9dcb3e9cap196652jsn0b2292b34189",
    	"X-RapidAPI-Host": "livescore6.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    return response.json()

@router.get("/news")
async def get_News(db: Session = Depends(get_db)):

    url = "https://livescore6.p.rapidapi.com/news/v2/list"
  
    headers = {
      "X-RapidAPI-Key": "f04a55b9a6msh71c0ad9dcb3e9cap196652jsn0b2292b34189",
      "X-RapidAPI-Host": "livescore6.p.rapidapi.com"
    }
  
    response = requests.get(url, headers=headers)
  
    return response.json()

@router.get("/stats")
async def get_stats(eid: str, sport: str, db: Session = Depends(get_db)):
  
    url = "https://livescore6.p.rapidapi.com/matches/v2/get-statistics"
    
    querystring = {"Category":sport,"Eid":eid}
    
    headers = {
    	"X-RapidAPI-Key": "f04a55b9a6msh71c0ad9dcb3e9cap196652jsn0b2292b34189",
    	"X-RapidAPI-Host": "livescore6.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    return response.json()

@router.get("/table")
async def get_table(eid: str, sport: str, db: Session = Depends(get_db)):
  
    url = "https://livescore6.p.rapidapi.com/matches/v2/get-scoreboard"

    querystring = {"Eid":eid,"Category":sport}
    
    headers = {
    	"X-RapidAPI-Key": "f04a55b9a6msh71c0ad9dcb3e9cap196652jsn0b2292b34189",
    	"X-RapidAPI-Host": "livescore6.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    return response.json()

@router.get("/live")
async def get_live(db: Session = Depends(get_db)):
  
    cookies = {
    'remixlang': '0',
    'remixstlid': '9063875395262911266_Agh8W3ZpDzkDcQxUSQ4nvo6M5OLNA2i97ZEzh1vQhpg',
    'remixstid': '1634662892_ZXG9i4tzS055JRreQsDc8FMyN3LbCXdYmxBjI4aes8z',
    'remixlgck': 'd296206a34d9a7ed4f',
    'remixnp': '0',
    'remixdt': '0',
    'remixdark_color_scheme': '1',
    'remixcolor_scheme_mode': 'auto',
    'remixua': '156%7C-1%7C311%7C610077997',
    'remixmdevice': '1920/1080/1/!!-!!!!!!!!',
    'remixff': '10101111111111',
    'remixmvk-fp': 'd7851b37de683cc89888d581f5b21240',
    'remixuacck': '52167b6340eb1b4d3d',
    'remixforce_full': '2',
    'remixshow_fvbar': '1',
    'remixbdr': '0',
    'remixuas': 'OWMzYjRlYWE4MDc1ZGUxY2ZiYjA3NTc0',
    'remixsts': '%7B%22data%22%3A%5B%5B1683121513%2C%22web_dark_theme%22%2C%22auto%22%2C%22vkcom_dark%22%2C1%5D%5D%2C%22uniqueId%22%3A543030476%7D',
    }
    
    headers = {
        'authority': 'vk.com',
        'accept': '*/*',
        'accept-language': 'ru',
        'content-type': 'application/x-www-form-urlencoded',
        # 'cookie': 'remixlang=0; remixstlid=9063875395262911266_Agh8W3ZpDzkDcQxUSQ4nvo6M5OLNA2i97ZEzh1vQhpg; remixstid=1634662892_ZXG9i4tzS055JRreQsDc8FMyN3LbCXdYmxBjI4aes8z; remixlgck=d296206a34d9a7ed4f; remixnp=0; remixdt=0; remixdark_color_scheme=1; remixcolor_scheme_mode=auto; remixua=156%7C-1%7C311%7C610077997; remixmdevice=1920/1080/1/!!-!!!!!!!!; remixff=10101111111111; remixmvk-fp=d7851b37de683cc89888d581f5b21240; remixuacck=52167b6340eb1b4d3d; remixforce_full=2; remixshow_fvbar=1; remixbdr=0; remixuas=OWMzYjRlYWE4MDc1ZGUxY2ZiYjA3NTc0; remixsts=%7B%22data%22%3A%5B%5B1683121513%2C%22web_dark_theme%22%2C%22auto%22%2C%22vkcom_dark%22%2C1%5D%5D%2C%22uniqueId%22%3A543030476%7D',
        'dnt': '1',
        'origin': 'https://vk.com',
        'referer': 'https://vk.com/video/lives/sport',
        'sec-ch-ua': '"Chromium";v="112", "Not_A Brand";v="24", "Opera";v="98"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; FreeBSD amd64; rv:108.0) Gecko/20100101 Firefox/108.0',
        'x-requested-with': 'XMLHttpRequest',
    }
    
    data = {
        'al': '1',
        'silent_loading': '1',
    }
    
    response = requests.post('https://vk.com/video/lives/sport', cookies=cookies, headers=headers, data=data)
    
    res = []
    resp = json.loads(response.json()['payload'][1][0])
    for i in resp["videos"]:
        temp = {"poster": i[2],
                "name": i[3]}
        for j in i:
            if "/video-" in str(j):
                temp["url"] = "https://vk.com" + j
        res.append(temp)

    return res
  
#@router.get("/get/{id}")
#async def get_album_songs(id: int, db: Session = Depends(get_db)):
#    return await crud.get_album_songs(id, db)


#@router.get("/{id}/songs")
#async def get_album_songs(id: int, db: Session = Depends(get_db)):
#    return await crud.get_album_songs(id, db)


#@router.post("/create/{name}/{description}")
#async def create_album(request: Request, name: str, description: str, data: schemas.AlbumData = Depends(schemas.AlbumData.form), db: Session = Depends(get_db)):
#    data.artist = get_jwt_sub(request)['id']
#    data.name = name
#    data.description = description
#    return await crud.create_album(data, db)


#@router.post("/add-track/{album}/{name}")
#async def add_track_to_album(album: int, name: str, request: Request,
 #                            data: schemas.SongData = Depends(schemas.SongData.form),
  #                           db: Session = Depends(get_db)):
   # data.artist = get_jwt_sub(request)['id']
    #data.name = name
    #data.album = album
   # print(data)
  #  return await crud.add_track_to_album(data, db)


#@router.delete("/remove-track/{id}")
#async def remove_track_from_album(request: Request, id: int, db: Session = Depends(get_db)):
#    user_id = get_jwt_sub(request)['id']
#    return await crud.remove_track_from_album(id, user_id, db)


#@router.delete("/delete/{id}")
#async def delete_album(request: Request, id: int, db: Session = Depends(get_db)):
#    user_id = get_jwt_sub(request)['id']
#    return await crud.remove_album(id, user_id, db)
