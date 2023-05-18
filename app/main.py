import json
from bcrypt import checkpw
from random import randint
from secrets import token_hex

from fastapi import FastAPI, Request, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

import json
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin import db
from fastapi import APIRouter

from app.funcs.utils import JWTSettings

app = APIRouter(prefix="/autosalon", tags=["Autosalon"])

swagger_url = token_hex(randint(10, 15))  # todo
app = FastAPI(title="Autosalon", version="0.5", docs_url=f"/docs")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@AuthJWT.load_config
def get_config():
    return JWTSettings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


def get_firedb(): 
    cred = credentials.Certificate('autosalon-8d839-firebase-adminsdk-y7e34-be7a9fb896.json')
    
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://autosalon-8d839-default-rtdb.europe-west1.firebasedatabase.app',
        'databaseAuthVariableOverride': {
            'uid': '1686344400000'
        }
    })

    return 

@app.get("/register")
async def add_users(login: str, password: str, authorize: AuthJWT = Depends()):
    ref = db.reference('/Users')
    us=ref.child(login).get()

    if us is None:
        data = {'groups': 'user','password': password}
        ref.child(login).set(data)

        data['login'] = login
        del data['password']
        data = authorize.create_refresh_token(json.dumps(data))
        response = JSONResponse({"token": str(data)})
        return response
    else:
        return JSONResponse(status_code=409, content={"detail": "User already exists"})


@app.get("/login")
async def add_login(login: str, password: str, authorize: AuthJWT = Depends()):
    ref = db.reference('/Users')
    data=ref.child(login).get()

    if data is None:
        return JSONResponse(status_code=404, content={"detail": "User not found"})

    data['login'] = login
    if password == data['password']:
        del data['password']
        data = authorize.create_refresh_token(json.dumps(data))
        response = JSONResponse({"token": str(data)})
        return response
    else:
        return  JSONResponse(status_code=403, content={"result": "Wrong password"})


@app.on_event("startup")
def startup():
    get_firedb()

#@app.get("/ads")
#async def get_Ads():
#    ref = db.reference('/Users')
#    ref1 = db.reference('/ads')
#    print(ref.get())
#    print(ref1.get())
#    return
#
#@app.get("/users")
#async def get_Users():
#    ref = db.reference('/Users')
#    ref1 = db.reference('/ads')
#    print(ref.get())
#    print(ref1.get())
#    return