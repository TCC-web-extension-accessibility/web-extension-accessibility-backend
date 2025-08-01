from io import BytesIO
from gtts import gTTS

class TextToSpeechService:
    def convert_text_to_audio(self, text: str, lang: str = "pt", tld='com.br') -> BytesIO:
        if not text.strip():
            raise ValueError("Text cannot be empty.")

        tts = gTTS(text=text, lang=lang, tld=tld)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        return audio_bytes