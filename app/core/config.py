import os
from dotenv import load_dotenv

load_dotenv()

#banco sqlite em memoria para testes
DATABASE_URL = "sqlite:///:memory:"

SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
