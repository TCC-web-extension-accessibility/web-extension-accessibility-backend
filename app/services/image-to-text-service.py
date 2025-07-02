from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

def encode_image(image_path):
    with Image.open(image_path) as img:
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

def describe_image(image_path):
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    image = Image.open(image_path).convert("RGB")

    prompt = "A photo showing"

    inputs = processor(image, text=prompt, return_tensors="pt")

    output = model.generate(**inputs, max_length=50, num_beams=5, early_stopping=True)

    caption = processor.decode(output[0], skip_special_tokens=True)

    return caption
    
if __name__ == "__main__":
    description = describe_image("./images_examples/monkey_holding_a_banana.jpg")
    print("Descrição gerada pela IA: \n", description)