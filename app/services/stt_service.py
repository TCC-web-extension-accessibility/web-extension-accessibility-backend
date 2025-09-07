import json
import logging
from typing import Dict, Any
from vosk import Model, KaldiRecognizer
import os

logger = logging.getLogger(__name__)

class STTService:
    def __init__(self):
        self.model = None
        self.recognizer = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Inicializa o modelo Vosk para português brasileiro"""
        try:
            # Tenta carregar modelo em português, fallback para inglês
            model_paths = [
                "../models/vosk-model-small-pt-0.3",
                "../models/vosk-model-pt-fb-v0.1.1",
                "../models/vosk-model-small-en-us-0.15"
            ]
            
            for model_path in model_paths:
                if os.path.exists(model_path):
                    self.model = Model(model_path)
                    self.recognizer = KaldiRecognizer(self.model, 16000)
                    logger.info(f"Modelo Vosk carregado: {model_path}")
                    break
            
            if not self.model:
                logger.warning("Nenhum modelo Vosk encontrado. STT offline não estará disponível.")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar modelo Vosk: {e}")
            self.model = None
            self.recognizer = None
    
    def transcribe_audio(self, audio_data: bytes, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Transcreve áudio para texto usando Vosk
        
        Args:
            audio_data: Dados de áudio em bytes
            sample_rate: Taxa de amostragem (padrão: 16000)
        
        Returns:
            Dict com texto transcrito e confiança
        """
        if not self.model or not self.recognizer:
            return {
                "success": False,
                "error": "Modelo STT não disponível",
                "text": "",
                "confidence": 0.0
            }
        
        try:
            # Processa o áudio
            self.recognizer.AcceptWaveform(audio_data)
            result = self.recognizer.FinalResult()
            
            # Parse do resultado JSON
            result_dict = json.loads(result)
            
            if result_dict.get("text", "").strip():
                return {
                    "success": True,
                    "text": result_dict["text"].strip(),
                    "confidence": result_dict.get("confidence", 0.0),
                    "language": "pt-BR" if "pt" in str(self.model) else "en-US"
                }
            else:
                return {
                    "success": False,
                    "error": "Nenhum texto detectado",
                    "text": "",
                    "confidence": 0.0
                }
                
        except Exception as e:
            logger.error(f"Erro na transcrição: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0
            }
    
    def is_available(self) -> bool:
        """Verifica se o serviço STT está disponível"""
        return self.model is not None and self.recognizer is not None 