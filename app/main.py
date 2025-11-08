from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.api.admin_routes import router as auth_router
from app.api.public_routes import router as public_router
from app.api.routes import router
from app.core.config import ALLOWED_ORIGIN
from app.core.init_db import create_tables, seed_initial_data

app = FastAPI()

create_tables()
seed_initial_data()

origins = [ALLOWED_ORIGIN]

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
)

app.include_router(auth_router, prefix="/admin", tags=["admin"])

app.include_router(public_router, prefix="/public", tags=["public"])

app.include_router(router,prefix="/api/v1", tags=["api"])

add_pagination(app)