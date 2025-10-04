from pydantic import BaseModel

class Feedback_schema(BaseModel):
    title: str
    message: str
