from random import randint
from secrets import token_hex

from fastapi import FastAPI, Request, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from sqlalchemy.orm import Session

from app.funcs.utils import JWTSettings
from app.tags import tags_metadata
from app.routers import auth, sports
from app.database import models, crud
from app.database.database import engine, SessionLocal
from app.dependencies import get_db, get_settings

settings = get_settings()
swagger_url = token_hex(randint(10, 15))  # todo
app = FastAPI(title="Audio", version="0.5", docs_url=f"/docs", redoc_url=None,
              dependencies=[Depends(get_db)], openapi_tags=tags_metadata)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(sports.router)


@AuthJWT.load_config
def get_config():
    return JWTSettings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


@app.on_event("startup")
def startup():
    # models.DataBase.metadata.drop_all(bind=engine)
    models.DataBase.metadata.create_all(bind=engine)
    with Session(engine) as db:
        # crud.preset(db)
        pass
