from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .auth.auth_routes import router as auth_router
from .core.init_db import create_tables,seed_initial_data
from .api.routes import router
from fastapi.middleware.cors import CORSMiddleware
from .core.config import ALLOWED_ORIGIN

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

app.include_router(auth_router, prefix="/auth", tags=["auth"])

app.include_router(router,prefix="/api/v1", tags=["api"])
