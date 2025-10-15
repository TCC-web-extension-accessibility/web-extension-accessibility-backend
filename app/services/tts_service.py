from io import BytesIO
from typing import Dict
from gtts import gTTS, gTTSError
from gtts.lang import tts_langs
import pyttsx3
import tempfile
import os
import time

class TextToSpeechService:
    async def convert_text_to_audio_async(self, text: str, lang: str = "pt") -> BytesIO:
        if text is None:
            raise ValueError("Text cannot be None.")
        if not isinstance(text, str):
            raise ValueError("Text must be a string.")
        if not text.strip():
            raise ValueError("Text cannot be empty.")

        if lang is None:
            raise ValueError("Language code cannot be None.")
        if not isinstance(lang, str):
            raise ValueError("Language code must be a string.")
        
        normalized_lang = lang.strip().lower().replace("_", "-")
        if not normalized_lang:
            raise ValueError("Language code cannot be empty.")

        supported_languages: Dict[str, str] = tts_langs()
        
        # Tenta usar gTTS primeiro
        try:
            if normalized_lang not in supported_languages:
                raise ValueError(f"Unsupported language: {normalized_lang}.")
            
            tts = gTTS(text=text, lang=normalized_lang)
            audio_bytes = BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            time.sleep(2)
            
            return audio_bytes

        except (gTTSError, Exception):
            # Usa fallback com pyttsx3 (offline)
            try:
                engine = pyttsx3.init()                
                engine.setProperty("rate", 150)
                engine.setProperty("volume", 1.0)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
                    temp_filename = tmpfile.name

                engine.save_to_file(text, temp_filename)
                engine.runAndWait()
                engine.stop()

                with open(temp_filename, "rb") as f:
                    audio_bytes = BytesIO(f.read())

                os.remove(temp_filename)
                audio_bytes.seek(0)

                return audio_bytes

            except Exception:
                raise ValueError("Erro ao gerar áudio.")  