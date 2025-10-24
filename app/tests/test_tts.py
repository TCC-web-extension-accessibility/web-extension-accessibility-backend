import pytest
from io import BytesIO
import asyncio
from app.services.tts_service import TextToSpeechService


class TestTextToSpeechService:
    @pytest.fixture
    def service(self):
        return TextToSpeechService()

    def test_convert_text_to_audio_empty_text(self, service):
        with pytest.raises(ValueError, match="Text cannot be empty."):
            asyncio.run(service.convert_text_to_audio_async("   "))

    def test_convert_text_to_audio_none_text(self, service):
        with pytest.raises(ValueError, match="Text cannot be None."):
            asyncio.run(service.convert_text_to_audio_async(None))

    def test_convert_text_to_audio_invalid_text_type(self, service):
        with pytest.raises(ValueError, match="Text must be a string."):
            asyncio.run(service.convert_text_to_audio_async(123))

    def test_convert_text_to_audio_none_lang(self, service):
        with pytest.raises(ValueError, match="Language code cannot be None."):
            asyncio.run(service.convert_text_to_audio_async("teste", None))

    def test_convert_text_to_audio_invalid_lang_type(self, service):
        with pytest.raises(ValueError, match="Language code must be a string."):
            asyncio.run(service.convert_text_to_audio_async("teste", 123))

    def test_convert_text_to_audio_empty_lang(self, service):
        with pytest.raises(ValueError, match="Language code cannot be empty."):
            asyncio.run(service.convert_text_to_audio_async("teste", "   "))

    @pytest.mark.parametrize("text", [
        "Olá, tudo bem?",
        "123456",
        "Texto com acentuação: é, à, õ, ç",
        "😄👍🎉",
        "Texto com símbolos !@#$%^&*()",
        "Este é um texto um pouco maior para testar a conversão de frases completas com pontuação."
    ])
    def test_convert_text_to_audio_valid_texts(self, service, text):
        result = asyncio.run(service.convert_text_to_audio_async(text, "pt"))
        assert isinstance(result, BytesIO)

