from pydantic import BaseModel
from typing import Optional

class VoiceCommand(BaseModel):
    intent: str
    action: str
    target: Optional[str] = None
    confidence: float = 0.0

class VoiceCommandRequest(BaseModel):
    text: str
    