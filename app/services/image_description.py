from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError
from app.core.config import AZURE_CV_KEY, AZURE_CV_ENDPOINT
from fastapi import HTTPException, status

client = ImageAnalysisClient(
    endpoint=AZURE_CV_ENDPOINT,
    credential=AzureKeyCredential(AZURE_CV_KEY)
)

def analyze_image(image_bytes: bytes) -> str:
    result = None
    try:
        result = client.analyze(
            image_data=image_bytes,
            visual_features=[VisualFeatures.CAPTION],
            gender_neutral_caption=True
        )
    except ClientAuthenticationError as authError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied due to invalid subscription key or wrong API endpoint.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
        
    if result and result.caption is not None:
        return {"caption": result.caption.text}
    else:
        return {"caption": "no caption"}
