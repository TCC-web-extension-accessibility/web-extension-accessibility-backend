import os
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig

load_dotenv()

#banco sqlite em memoria para testes
DATABASE_URL = "sqlite:///:memory:"

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

AZURE_TRANSLATE_API_KEY = os.getenv("AZURE_API_TRANSLATE_KEY")
AZURE_TRANSLATE_API_ENDPOINT = os.getenv("AZURE_API_TRANSLATE_ENDPOINT")
AZURE_API_REGION = os.getenv("AZURE_API_REGION")

AZURE_CV_KEY = os.getenv("AZURE_CV_KEY")
AZURE_CV_ENDPOINT = os.getenv("AZURE_CV_ENDPOINT")

ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN")

WITAI_TOKEN = os.getenv("WITAI_TOKEN")

FRONTENTD_HOST = os.getenv("FRONTENTD_HOST")
FRONTEND_FORGET_PASSWORD_URL = os.getenv("FRONTEND_FORGET_PASSWORD_URL")

MAIL_CONF = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    TEMPLATE_FOLDER="app/templates"
)