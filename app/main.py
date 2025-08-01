from fastapi import FastAPI
from auth.auth_routes import router as auth_router
from api.tts import router as tts_router
from core.init_db import create_tables,seed_initial_data

app = FastAPI()

create_tables()
seed_initial_data()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(tts_router, prefix="/tts", tags=["text to audio"])