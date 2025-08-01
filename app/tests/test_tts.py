import pytest
import tempfile
import pygame
import time
import os
from app.services.tts_service import TextToSpeechService

class TestTextToSpeechService:
    def setup_method(self):
        self.service = TextToSpeechService()
        
    def test_convert_text_to_audio_empty_text(self):
        with pytest.raises(ValueError, match="Text cannot be empty."):
            self.service.convert_text_to_audio("   ")

    @pytest.mark.parametrize("text", [
        "Olá, tudo bem?",
        "123456",
        "Texto com acentuação: é, à, õ, ç",
        "😄👍🎉",
        "Texto com símbolos !@#$%^&*()",
        "Este é um texto um pouco maior para testar a conversão de frases completas com pontuação."
    ])
    @pytest.mark.parametrize("lang", ["pt"])
    def test_convert_text_to_audio_and_play(self, text, lang):
        audio_bytes_io = self.service.convert_text_to_audio(text, lang)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(audio_bytes_io.read())
            temp_file_path = temp_file.name

        try:
            if os.getenv("PLAY_AUDIO", "0") == "1":
                pygame.mixer.init()
                pygame.mixer.music.load(temp_file_path)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.2)

                pygame.mixer.music.stop()
                pygame.mixer.quit()
        finally:
            os.remove(temp_file_path)