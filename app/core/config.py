import os
from dotenv import load_dotenv

load_dotenv()

#banco sqlite em memoria para testes
DATABASE_URL = "sqlite:///:memory:"

SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

AZURE_TRANSLATE_API_KEY = os.getenv("AZURE_API_TRANSLATE_KEY")
AZURE_TRANSLATE_API_ENDPOINT = os.getenv("AZURE_API_TRANSLATE_ENDPOINT")
AZURE_TRANSLATE_API_REGION = os.getenv("AZURE_API_TRANSLATE_REGION")