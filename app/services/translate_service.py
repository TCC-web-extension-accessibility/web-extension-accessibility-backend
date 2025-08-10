import requests, uuid, json
from app.core.config import AZURE_TRANSLATE_API_ENDPOINT, AZURE_TRANSLATE_API_KEY, AZURE_TRANSLATE_API_REGION

key = AZURE_TRANSLATE_API_KEY 
endpoint = AZURE_TRANSLATE_API_ENDPOINT 
location = AZURE_TRANSLATE_API_REGION 

def translate_text(text, to_language):
    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': [to_language] 
    }

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{
        'text': text 
    }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()

    print(json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))