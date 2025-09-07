from fastapi import APIRouter, File, UploadFile, HTTPException, Response, status
from fastapi import WebSocket, WebSocketDisconnect
from schemas.translation_schema import Translation_schema
from services.translate_service import translate_list
from services.image_description import analyze_image
from services.tts_service import TextToSpeechService
from services.websocket_service import WebSocketManager
from asyncio.log import logger
import uuid

router = APIRouter()
websocket_manager = WebSocketManager()

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

@router.websocket("/voice-navigation/")
async def voice_navigation_websocket(websocket: WebSocket):
    """WebSocket para navegação por voz em tempo real"""
    client_id = str(uuid.uuid4())
    
    try:
        await websocket_manager.connect(websocket, client_id)
        
        while True:
            # Recebe mensagem do cliente
            message = await websocket.receive_text()
            await websocket_manager.handle_message(websocket, client_id, message)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"Erro na conexão WebSocket: {e}")
        websocket_manager.disconnect(client_id)