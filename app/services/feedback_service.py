from app.models.feedback_model import Feedback_model
from app.schemas.feedback_schema import Feedback_request_schema
from datetime import datetime
from app.repositories.impl.feedback_repository_impl import FeedbackRepositoryImpl
from sqlalchemy.orm import Session

def send_feedback(feedback: Feedback_request_schema, db: Session) -> None:
    repository = FeedbackRepositoryImpl(db)
    feedback_data = Feedback_model(
        title=feedback.title,
        message=feedback.message,
        timestamp=datetime.now()
    )
    repository.add(feedback_data)

def get_paginated_feedbacks(db: Session):
    repository = FeedbackRepositoryImpl(db)
    return repository.get_paginated()