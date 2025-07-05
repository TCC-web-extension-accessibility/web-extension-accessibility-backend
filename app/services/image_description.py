from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes

def describe_image(client, file_path):
    with open(file_path, "rb") as image_stream:
        analysis = client.analyze_image_in_stream(
            image_stream, 
            visual_features=[VisualFeatureTypes.description],
            language = 'pt'
        )
    description = ''
    if analysis.description and analysis.description.captions:
        description = ' '.join([caption.text for caption in analysis.description.captions])
    else:
        description = 'Nenhuma descrição encontrada.'
    return description 
