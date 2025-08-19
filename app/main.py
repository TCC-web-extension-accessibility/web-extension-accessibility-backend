from fastapi import FastAPI
from auth.auth_routes import router as auth_router
from core.init_db import create_tables,seed_initial_data
from api.routes import router

app = FastAPI()

create_tables()
seed_initial_data()

app.include_router(auth_router, prefix="/auth", tags=["auth"])

app.include_router(router,prefix="/api/v1", tags=["api"])