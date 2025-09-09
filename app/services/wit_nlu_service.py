import os
import requests
from typing import Optional
from dataclasses import dataclass

@dataclass
class VoiceCommand:
    intent: str
    action: str
    target: Optional[str] = None
    confidence: float = 0.0

class WitNLUService:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("WITAI_TOKEN")
        if not self.token:
            raise RuntimeError("WITAI_TOKEN não configurado nas variáveis de ambiente.")
        self.api_url = "https://api.wit.ai/message"

    def process_command(self, text: str, language: str = "auto") -> VoiceCommand:
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {"q": text}
        # Wit.ai detecta idioma automaticamente, mas pode ser treinado para vários idiomas
        response = requests.get(self.api_url, headers=headers, params=params)
        data = response.json()
        
        # Extração de intent e confidence
        intent = None
        confidence = 0.0
        if "intents" in data and data["intents"]:
            intent = data["intents"][0]["name"]
            confidence = data["intents"][0]["confidence"]
        
        # Extração de entidades com formato entity_name:role
        action = None
        target = None
        
        entities = data.get("entities", {})
        
        # Processar todas as entidades no formato entity_name:role
        for entity_key, entity_list in entities.items():
            if not entity_list:
                continue
                
            entity_data = entity_list[0]  # Pegar a primeira entidade com maior confidence
            entity_name = entity_data.get("name")
            entity_role = entity_data.get("role")
            entity_value = entity_data.get("value")
            
            # Mapear entidades para campos do VoiceCommand
            if entity_name == "browse_elements":
                # Tipos: navigate_next, navigate_previous, navigate_to
                action = entity_role
                if entity_role in ["navigate_next", "navigate_previous", "navigate_to"]:
                    target = entity_value
                    
            elif entity_name == "zoom":
                # Tipos: zoom_in, zoom_out
                action = entity_role
                target = entity_value
                
            elif entity_name == "get_value":
                # Tipo: value - usado para identificar elementos específicos
                if entity_role == "value":
                    target = entity_value
                    
            elif entity_name == "scroll":
                # Para comandos de scroll
                action = entity_role
                target = entity_value
        
        # Fallback: se não houver action específica, use intent como action
        if not action and intent:
            action = intent
        
        return VoiceCommand(
            intent=intent or "unknown",
            action=action or "unknown",
            target=target,
            confidence=confidence
        )
