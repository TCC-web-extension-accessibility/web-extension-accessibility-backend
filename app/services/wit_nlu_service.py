import requests
import logging
from typing import Optional, Dict, List, Tuple, Any
from schemas.voice_command_schema import VoiceCommand
from core.config import WITAI_TOKEN

logger = logging.getLogger(__name__)

class WitNLUConfig:    
    INTENTS = ['click', 'go_back', 'navigate', 'read', 'show_help', 'zoom']    
    ENTITIES = ['browse_elements', 'get_value', 'scroll', 'zoom']
    
    # Combined entity-intent-roles mapping
    ENTITY_INTENT_ROLES = {
        ('browse_elements', 'navigate'): ['navigate_previous', 'navigate_next', 'navigate_to'],
        ('get_value', 'click'): ['value'],
        ('get_value', 'read'): ['value'],
        ('scroll', 'navigate'): ['scroll_up', 'scroll_down', 'scroll_right', 'scroll_left'],
        ('zoom', 'zoom'): ['zoom_out', 'zoom_in']
    }

class EntityProcessor:
        
    def process(self, entity_data: Dict[str, Any], intent: str) -> Tuple[Optional[str], Optional[str]]:
        raise NotImplementedError

class BrowseElementsProcessor(EntityProcessor):
    """Processor for browse_elements entity"""
    
    def process(self, entity_data: Dict[str, Any], intent: str) -> Tuple[Optional[str], Optional[str]]:
        if intent != 'navigate':
            return None, None
            
        entity_role = entity_data.get('role')
        entity_value = entity_data.get('value')
        
        if entity_role in ['navigate_next', 'navigate_previous']:
            return entity_role, None
        elif entity_role == 'navigate_to':
            return entity_role, entity_value
            
        return None, None

class GetValueProcessor(EntityProcessor):
    """Processor for get_value entity"""
    
    def process(self, entity_data: Dict[str, Any], intent: str) -> Tuple[Optional[str], Optional[str]]:
        if intent not in ['click', 'read']:
            return None, None
            
        entity_role = entity_data.get('role')
        entity_value = entity_data.get('value')
        
        if entity_role == 'value':
            return intent, entity_value
            
        return None, None

class ScrollProcessor(EntityProcessor):
    """Processor for scroll entity"""
    
    def process(self, entity_data: Dict[str, Any], intent: str) -> Tuple[Optional[str], Optional[str]]:
        if intent != 'navigate':
            return None, None
            
        entity_role = entity_data.get('role')
        entity_value = entity_data.get('value')
        
        if entity_role in ['scroll_up', 'scroll_down', 'scroll_right', 'scroll_left']:
            return entity_role, entity_value
            
        return None, None

class ZoomProcessor(EntityProcessor):
    """Processor for zoom entity"""
    
    def process(self, entity_data: Dict[str, Any], intent: str) -> Tuple[Optional[str], Optional[str]]:
        if intent != 'zoom':
            return None, None
            
        entity_role = entity_data.get('role')
        entity_value = entity_data.get('value')
        
        if entity_role in ['zoom_in', 'zoom_out']:
            return entity_role, entity_value
            
        return None, None

class WitNLUService:
    """Service for processing natural language commands using Wit.ai"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or WITAI_TOKEN
        if not self.token:
            raise RuntimeError("WITAI_TOKEN not configured in environment variables")
        self.api_url = "https://api.wit.ai/message"
        
        # Initialize entity processors
        self.entity_processors = {
            'browse_elements': BrowseElementsProcessor(),
            'get_value': GetValueProcessor(),
            'scroll': ScrollProcessor(),
            'zoom': ZoomProcessor()
        }
    
    def _make_wit_request(self, text: str) -> Dict[str, Any]:
        """Make request to Wit.ai API"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            params = {"q": text}
            response = requests.get(self.api_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to Wit.ai: {e}")
            raise RuntimeError(f"Falha na comunicação com Wit.ai: {e}")
    
    def _extract_intent_and_confidence(self, data: Dict[str, Any]) -> Tuple[Optional[str], float]:
        """Extract intent and confidence from Wit.ai response"""
        if "intents" not in data or not data["intents"]:
            return None, 0.0
            
        intent_data = data["intents"][0]
        intent = intent_data.get("name")
        confidence = intent_data.get("confidence", 0.0)
        
        # Validate intent
        if intent not in WitNLUConfig.INTENTS:
            logger.warning(f"Unknown intent received: {intent}")
            return None, confidence
            
        return intent, confidence
    
    def _process_entities(self, entities: Dict[str, List[Dict[str, Any]]], intent: str) -> Tuple[Optional[str], Optional[str]]:
        """Process entities using appropriate processors"""
        action = None
        target = None
        
        for entity_key, entity_list in entities.items():
            if not entity_list:
                continue
                
            entity_data = entity_list[0]
            entity_name = entity_data.get("name")
            
            # Validate entity
            if entity_name not in WitNLUConfig.ENTITIES:
                logger.warning(f"Unknown entity received: {entity_name}")
                continue
            
            # Validate entity-intent combination
            if intent and (entity_name, intent) not in WitNLUConfig.ENTITY_INTENT_ROLES:
                logger.debug(f"Entity {entity_name} not valid for intent {intent}")
                continue
            
            # Process entity
            processor = self.entity_processors.get(entity_name)
            if processor:
                processed_action, processed_target = processor.process(entity_data, intent)
                if processed_action:
                    action = processed_action
                    target = processed_target
                    break  # Use first valid entity processing result
        
        return action, target
    
    def _handle_special_intents(self, intent: str, action: str, target: str) -> Tuple[Optional[str], Optional[str]]:
        """Handle special intent processing rules"""
        # Handle click without target
        if intent == "click" and not target:
            return None, None
            
        # Handle read with target
        if intent == "read" and target:
            return intent, target
            
        # Handle simple intents
        if intent in ["go_back", "show_help"]:
            return intent, target
            
        return action, target
    
    def process_command(self, text: str) -> VoiceCommand:
        """Process natural language command and return structured VoiceCommand"""
        if not text or not text.strip():
            logger.warning("Empty text provided for processing")
            return VoiceCommand(
                intent="unknown",
                action="unknown",
                target=None,
                confidence=0.0
            )
        
        try:
            # Make request to Wit.ai
            data = self._make_wit_request(text.strip())
            logger.debug(f"Wit.ai response for '{text}': {data}")
            
            # Extract intent and confidence
            intent, confidence = self._extract_intent_and_confidence(data)
            
            # Process entities
            entities = data.get("entities", {})
            action, target = self._process_entities(entities, intent)
            
            # Handle special intent rules
            final_action, final_target = self._handle_special_intents(intent, action, target)
            
            # Create result
            result = VoiceCommand(
                intent=intent or "unknown",
                action=final_action or "unknown",
                target=final_target,
                confidence=confidence
            )
            
            logger.info(f"Processed command '{text}' -> {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing command '{text}': {e}")
            return VoiceCommand(
                intent="unknown",
                action="unknown",
                target=None,
                confidence=0.0
            )
