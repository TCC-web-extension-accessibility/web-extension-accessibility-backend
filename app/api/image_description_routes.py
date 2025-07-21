from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from services.image_description import ImageDescriptionService
import os

router = APIRouter()

# Load environment credentials
endpoint = os.getenv("AZURE_CV_ENDPOINT")
key = os.getenv("AZURE_CV_KEY")

if not endpoint or not key:
    raise RuntimeError("AZURE_CV_ENDPOINT and AZURE_CV_KEY must be set in .env")

img_service = ImageDescriptionService(endpoint, key)

@router.post("/describe-image/")
async def describe_image(file: UploadFile = File(...)):
    if file.content_type.split('/')[0] != 'image':
        raise HTTPException(status_code=400, detail="File must be an image")

    image_bytes = await file.read()
    description = img_service.describe_image_bytes(image_bytes)

    if description is None:
        return JSONResponse(status_code=500, content={"error": "Could not generate description"})

    return {"description": description}
