from json import loads

from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from app.dependencies import get_settings

settings = get_settings()


class JWTSettings(BaseModel):
    authjwt_secret_key: str = settings.secret


def get_jwt_sub(request, cookie: str = None):
    if cookie is not None:
        request.headers.__dict__["_list"].append(("authorization".encode(), f"Bearer {cookie}".encode()))
    authorize = AuthJWT(request)
    try:
        return loads(authorize.get_jwt_subject())
    except Exception as e:
        raise HTTPException(status_code=403)
