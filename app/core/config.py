import os
from dotenv import load_dotenv
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

from services import ocr
from services import image_description

load_dotenv()

#banco sqlite em memoria para testes
DATABASE_URL = "sqlite:///:memory:"

SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Inicialização do Azure Credentials
key = os.getenv('AZURE_CV_KEY')
endpoint = os.getenv('AZURE_CV_ENDPOINT')

client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

# Validação se as variáveis estão no dotenv
if not key or not endpoint:
    raise ValueError("As variáveis AZURE_CV_KEY ou AZURE_CV_ENDPOINT não estão definidas no .env")


