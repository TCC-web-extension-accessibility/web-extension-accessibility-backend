from fastapi import FastAPI
from app.api.admin_routes import router as auth_router
from app.core.init_db import create_tables,seed_initial_data
from app.api.routes import router
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import ALLOWED_ORIGIN
from fastapi_pagination import add_pagination

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

app.include_router(router,prefix="/api/v1", tags=["api"])

add_pagination(app)