from json import dumps

from fastapi import APIRouter, Depends, UploadFile, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app.database import crud, schemas
from app.dependencies import get_db
from app.funcs.utils import get_jwt_sub

router = APIRouter(prefix="/auth", tags=["Identity"])


@router.get("/")
async def login(username: str, password: str, authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    data = schemas.UserData(login=username, password=password)
    db_data = await crud.login(data, db)
    if not db_data:
        return JSONResponse(status_code=403, content={"result": "Wrong password"})
    if db_data is None:
        return JSONResponse(status_code=404, content={"detail": "User not found"})
    response = JSONResponse({"token": str(authorize.create_refresh_token(dumps({"id": db_data.id,
                                                                                "login": db_data.login})))})
    return response


@router.post("/")
async def register(data: schemas.UserData, authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    for i in data.login:
        if ord(i) < 33 or ord(i) > 123:
            return JSONResponse(status_code=409, content={"detail": "Unsupported symbols"})
    db_data = await crud.register(data, db)
    if not db_data:
        return JSONResponse(status_code=409, content={"detail": "User already exists"})
    response = JSONResponse({"token": str(authorize.create_refresh_token(dumps({"id": db_data.id,
                                                                                "login": db_data.login})))})
    return response


@router.post("/image")
async def upload_image(request: Request, data: UploadFile, db: Session = Depends(get_db)):
    user_id = get_jwt_sub(request)['id']
    await crud.set_image(await data.read(), user_id, data.filename, db)
    return JSONResponse(status_code=200, content={"result": "OK"})


@router.get("/me")
async def upload_image(request: Request, db: Session = Depends(get_db)):
    user_id = get_jwt_sub(request)['id']
    return await crud.get_my_data(user_id, db)
