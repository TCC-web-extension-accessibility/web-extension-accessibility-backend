from io import BytesIO
from typing import Dict
from gtts import gTTS
from gtts.lang import tts_langs

class TextToSpeechService:
    def convert_text_to_audio(self, text: str, lang: str = "pt") -> BytesIO:
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
        if normalized_lang not in supported_languages:
            raise ValueError(f"Unsupported language: {normalized_lang}.")

        tts = gTTS(text=text, lang=normalized_lang)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)

        return audio_bytes