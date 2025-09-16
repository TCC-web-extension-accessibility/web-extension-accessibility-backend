from fastapi import APIRouter, File, UploadFile, HTTPException, Response, status
from schemas.translation_schema import Translation_schema
from schemas.voice_command_schema import VoiceCommandRequest
from services.translate_service import translate_list
from services.image_description import analyze_image
from services.tts_service import TextToSpeechService
from services.wit_nlu_service import WitNLUService

router = APIRouter()

@router.post("/translate/")
async def translate_text_list(translate_body: Translation_schema):
    return translate_list(
        to_language=translate_body.to_language,
        text_list=translate_body.text_list,
        from_language=translate_body.from_language
    )

@router.post("/describe-image/")
async def describe_image(file: UploadFile = File(...)):
    if file.content_type.split('/')[0] != 'image':
        raise HTTPException(status_code=400, detail="File must be an image")
    
    image_bytes = await file.read()
    caption = analyze_image(image_bytes)

    return caption  

@router.post("/convert-audio/", response_class=Response)
def convert_audio(text: str) -> Response:
    tts_service = TextToSpeechService()
    try:
        audio_bytes = tts_service.convert_text_to_audio(text)
        return Response(
            content=audio_bytes.read(),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=audio.mp3"},
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error generating audio.",
        )

@router.post("/voice-navigation/command")
def process_voice_command(request: VoiceCommandRequest):
    nlu_service = WitNLUService()
    command = nlu_service.process_command(request.text)
    return command