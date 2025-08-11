from fastapi import APIRouter
from schemas.translation_schema import Translation_schema
from services.translate_service import translate_list

router = APIRouter()

@router.post("/translate/")
async def translate_text_list(translate_body: Translation_schema):
    return translate_list(
        to_language=translate_body.to_language,
        text_list=translate_body.text_list,
        from_language=translate_body.from_language
        ) 