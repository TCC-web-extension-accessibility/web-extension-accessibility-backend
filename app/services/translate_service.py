import requests, uuid, json
from app.core.config import AZURE_TRANSLATE_API_ENDPOINT, AZURE_TRANSLATE_API_KEY, AZURE_API_REGION
from fastapi import HTTPException

def translate_list(to_language, text_list, from_language=None):
    path = '/translate'
    constructed_url = AZURE_TRANSLATE_API_ENDPOINT + path

    params = {
        'api-version': '3.0',
        'to': [to_language]
    }
    if from_language:
        params['from'] = from_language

    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_TRANSLATE_API_KEY,
        'Ocp-Apim-Subscription-Region': AZURE_API_REGION,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{'text': text} for text in text_list]

    response = requests.post(constructed_url, params=params, headers=headers, json=body)

    if response.status_code != 200:
        #gerar um log do erro
        raise HTTPException(status_code=response.status_code, detail=response.text)

    translations = response.json()
    #gear um log do sucesso
    return {orig: trans['translations'][0]['text'] for orig, trans in zip(text_list, translations)}
