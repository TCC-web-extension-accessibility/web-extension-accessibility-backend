import os 
from dotenv import load_dotenv
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes

load_dotenv()

ENDPOINT = os.getenv("AZURE_CV_ENDPOINT")
KEY = os.getenv("AZURE_CV_KEY")

if not ENDPOINT or not KEY:
    raise RuntimeError("As variáveis de ambiente AZURE_VISION_ENDPOINT e AZURE_VISION_KEY não foram definidas.")

computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))

def analyze_image_colors(image_stream) -> dict:
    """
    Envia uma imagem para a IA do Azure e retorna uma análise de cor detalhada. 
    """
    try:
        analysis = computervision_client.analyze_image_in_stream(
            image_stream,
            visual_features=[VisualFeatureTypes.color]
        )

        color_info = {
            "is_black_and_white": analysis.color.is_bw_img,
            "accent_color": f"#{analysis.color.accent_color}",
            "dominant_background": analysis.color.dominant_color_background,
            "dominant_foreground": analysis.color.dominant_color_foreground,
            "dominant_colors": analysis.color.dominant_colors,
        }

        return color_info
    except Exception as e:
        print(f"Erro ao chamar a API do Azure: {e}")
        raise

def suggest_filter(color_info: dict, blindness_type: str) -> str:
    """
    Usa os dados da IA pra fazer uma sugestão de filtro.
    """
    all_colors = set(color_info["dominant_colors"])
    all_colors.add(color_info["dominant_background"])
    all_colors.add(color_info["dominant_foreground"])

    if blindness_type in ["protanopia", "deuteranopia"]:
        has_red = any(color in ["Red", "Orange"] for color in all_colors)
        has_green = any(color in ["Green", "Teal"] for color in all_colors)

        if has_red and has_green:
            return "protaanopia-assist"
        
    return "no-filter"