import json
import logging
from typing import Dict, Any, Callable
from fastapi import WebSocket
from services.stt_service import STTService
from services.nlu_service import NLUService

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.stt_service = STTService()
        self.nlu_service = NLUService()
        self.message_handlers: Dict[str, Callable] = {
            "audio_data": self._handle_audio_data,
            "text_command": self._handle_text_command,
            "ping": self._handle_ping,
            "get_status": self._handle_get_status
        }
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Conecta um novo cliente WebSocket"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Cliente conectado: {client_id}")
        
        # Envia status inicial
        await self._send_message(websocket, {
            "type": "connection_status",
            "status": "connected",
            "client_id": client_id,
            "stt_available": self.stt_service.is_available(),
            "supported_commands": self._get_supported_commands()
        })
    
    def disconnect(self, client_id: str):
        """Desconecta um cliente"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Cliente desconectado: {client_id}")
    
    async def _send_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Envia mensagem para um cliente específico"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Envia mensagem para todos os clientes conectados"""
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await self._send_message(websocket, message)
            except Exception as e:
                logger.error(f"Erro ao enviar broadcast para {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Remove clientes desconectados
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def handle_message(self, websocket: WebSocket, client_id: str, message: str):
        """Processa mensagem recebida de um cliente"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type in self.message_handlers:
                await self.message_handlers[message_type](websocket, client_id, data)
            else:
                await self._send_message(websocket, {
                    "type": "error",
                    "message": f"Tipo de mensagem não suportado: {message_type}"
                })
                
        except json.JSONDecodeError:
            await self._send_message(websocket, {
                "type": "error",
                "message": "Formato JSON inválido"
            })
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            await self._send_message(websocket, {
                "type": "error",
                "message": f"Erro interno: {str(e)}"
            })
    
    async def _handle_audio_data(self, websocket: WebSocket, client_id: str, data: Dict[str, Any]):
        """Processa dados de áudio recebidos"""
        try:
            audio_data = data.get("audio_data")
            sample_rate = data.get("sample_rate", 16000)
            
            if not audio_data:
                await self._send_message(websocket, {
                    "type": "error",
                    "message": "Dados de áudio não fornecidos"
                })
                return
            
            # Converte base64 para bytes
            import base64
            audio_bytes = base64.b64decode(audio_data)
            
            # Transcreve o áudio
            transcription = self.stt_service.transcribe_audio(audio_bytes, sample_rate)
            
            if transcription["success"]:
                # Processa o comando com NLU
                command = self.nlu_service.process_command(transcription["text"])
                
                await self._send_message(websocket, {
                    "type": "transcription_result",
                    "transcription": transcription,
                    "command": {
                        "intent": command.intent,
                        "action": command.action,
                        "target": command.target,
                        "confidence": command.confidence
                    }
                })
            else:
                await self._send_message(websocket, {
                    "type": "transcription_error",
                    "error": transcription["error"]
                })
                
        except Exception as e:
            logger.error(f"Erro ao processar áudio: {e}")
            await self._send_message(websocket, {
                "type": "error",
                "message": f"Erro ao processar áudio: {str(e)}"
            })
    
    async def _handle_text_command(self, websocket: WebSocket, client_id: str, data: Dict[str, Any]):
        """Processa comando de texto direto"""
        try:
            text = data.get("text", "")
            
            if not text:
                await self._send_message(websocket, {
                    "type": "error",
                    "message": "Texto do comando não fornecido"
                })
                return
            
            # Processa o comando com NLU
            command = self.nlu_service.process_command(text)
            
            await self._send_message(websocket, {
                "type": "command_result",
                "command": {
                    "intent": command.intent,
                    "action": command.action,
                    "target": command.target,
                    "confidence": command.confidence
                }
            })
            
        except Exception as e:
            logger.error(f"Erro ao processar comando de texto: {e}")
            await self._send_message(websocket, {
                "type": "error",
                "message": f"Erro ao processar comando: {str(e)}"
            })
    
    async def _handle_ping(self, websocket: WebSocket, client_id: str, data: Dict[str, Any]):
        """Responde a ping para manter conexão ativa"""
        await self._send_message(websocket, {
            "type": "pong",
            "timestamp": data.get("timestamp")
        })
    
    async def _handle_get_status(self, websocket: WebSocket, client_id: str, data: Dict[str, Any]):
        """Retorna status atual dos serviços"""
        await self._send_message(websocket, {
            "type": "status",
            "stt_available": self.stt_service.is_available(),
            "supported_commands": self._get_supported_commands(),
            "active_connections": len(self.active_connections)
        })
    
    def _get_supported_commands(self) -> Dict[str, Any]:
        """Retorna comandos suportados para o frontend"""
        return {
            "navegação": [
                "ir para [elemento]",
                "rolar para baixo/cima/esquerda/direita",
                "próximo/anterior elemento",
                "primeiro/último elemento"
            ],
            "interação": [
                "clicar em [elemento]",
                "botão [nome]",
                "número [índice]"
            ],
            "leitura": [
                "ler [elemento]",
                "ler página",
                "o que é [elemento]"
            ],
            "sistema": [
                "ajuda",
                "voltar",
                "aumentar/diminuir zoom"
            ]
        } 