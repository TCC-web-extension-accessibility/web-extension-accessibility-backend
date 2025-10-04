from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.feedback_model import Feedback_model
from app.schemas.feedback_schema import Feedback_schema

def send_feedback(title, message):
    db: Session = SessionLocal()
    feedback = Feedback_model(
            title=title,
            message=message
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    db.close()
    return Feedback_schema(title=title, message=message)
