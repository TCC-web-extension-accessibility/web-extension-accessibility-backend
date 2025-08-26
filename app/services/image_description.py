from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from io import BytesIO
from typing import Optional

class ImageDescriptionService:
    def __init__(self, endpoint: str, key: str):
        self.client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

    def describe_image_bytes(self, image_bytes: bytes) -> Optional[str]:
        try:
            image_stream = BytesIO(image_bytes)
            description_result = self.client.describe_image_in_stream(image_stream, max_candidates=1)
            if description_result.captions:
                return description_result.captions[0].text
            else:
                return "No description found."
        except Exception as e:
            print(f"Error describing image: {e}")
            return None
