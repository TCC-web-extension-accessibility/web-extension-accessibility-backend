from fastapi import APIRouter, HTTPException, Response, status
from app.services.tts_service import TextToSpeechService

router = APIRouter()
tts_service = TextToSpeechService()

@router.post("/convert-audio", response_class=Response)
def convert_audio(text: str) -> Response:
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