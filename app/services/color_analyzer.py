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

def hex_to_rgb(hex_color):
    """Converte um código de cor hexadecimanl para uma tupla (R, G, B)."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return(0, 0, 0)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def suggest_filter(color_info: dict, blindness_type: str) -> str:
    """
    Usa os dados da IA pra fazer uma sugestão de filtro.
    """
    if blindness_type not in ["protanopia", "deuteranopia"]:
        return "no-filter"

    accent_rgb = hex_to_rgb(color_info["accent_color"])
    r, g, b = accent_rgb

    is_reddish = r > (g + b) * 0.8 and r > 80
    is_greenish = g > (r + b) * 0.8 and g > 80
    is_ambiguos = (r > 180 or g > 100) and abs(r - g) < 60 and (r + g > b * 2)

    if is_reddish or is_greenish or is_ambiguos:
        return "protanopia-assist"
    
    all_colors = set(color_info["dominant_colors"])
    has_red_family = any(c in ["Red", "Orange", "Brown", "Maroon"] for c in all_colors)
    has_green_family = any(c in ["Green", "Teal", "Olive", "Lime"] for c in all_colors)

    if has_red_family and has_green_family:
        return "protanopia-assist"
    
    return "no-filter"