from pydantic import BaseModel
from datetime import datetime

class Feedback_request_schema(BaseModel):
    title: str
    message: str

class Feedback_response_schema(BaseModel):
    title: str
    message: str
    timestamp: datetime