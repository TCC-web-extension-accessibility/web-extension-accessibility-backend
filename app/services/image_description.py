from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from core.config import AZURE_CV_KEY, AZURE_CV_ENDPOINT

client = ImageAnalysisClient(
    endpoint=AZURE_CV_ENDPOINT,
    credential=AzureKeyCredential(AZURE_CV_KEY)
)

def analyze_image(image_bytes: bytes) -> str:

    try:
        result = client.analyze(
            image_data=image_bytes,
            visual_features=[VisualFeatures.CAPTION],
            gender_neutral_caption=True
        )
    except Exception as e:
        print(f"Status code: {e.status_code}")
        print(f"Reason: {e.reason}")
        print(f"Message: {e.error.message}")

    if result.caption is not None:
        return {"caption": result.caption.text}
    else:
        return {"caption": "no caption"}