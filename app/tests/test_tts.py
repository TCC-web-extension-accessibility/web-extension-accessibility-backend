import asyncio
import pytest
import tempfile
import os
from app.services.tts_service import TextToSpeechService


class TestTextToSpeechService:
    def setup_method(self):
        self.service = TextToSpeechService()

    def test_convert_text_to_audio_empty_text(self):
        with pytest.raises(ValueError, match="Text cannot be empty."):
            asyncio.run(self.service.convert_text_to_audio_async("   "))

    def test_convert_text_to_audio_none_text(self):
        with pytest.raises(ValueError, match="Text cannot be None."):
            asyncio.run(self.service.convert_text_to_audio_async(None))

    def test_convert_text_to_audio_invalid_language(self):
        with pytest.raises(ValueError, match="Unsupported language: xx."):
            asyncio.run(self.service.convert_text_to_audio_async("teste", "xx"))

    @pytest.mark.parametrize("text", [
        "Olá, tudo bem?",
        "123456",
        "Texto com acentuação: é, à, õ, ç",
        "😄👍🎉",
        "Texto com símbolos !@#$%^&*()",
        "Este é um texto um pouco maior para testar a conversão de frases completas com pontuação."
    ])
    @pytest.mark.parametrize("lang", ["pt"])
    def test_convert_text_to_audio_produces_audio_bytes(self, text, lang):
        audio_bytes_io = asyncio.run(self.service.convert_text_to_audio_async(text, lang))

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(audio_bytes_io.read())
            temp_file_path = temp_file.name

        try:
            assert os.path.exists(temp_file_path)
            assert os.path.getsize(temp_file_path) > 0
        finally:
            os.remove(temp_file_path)
