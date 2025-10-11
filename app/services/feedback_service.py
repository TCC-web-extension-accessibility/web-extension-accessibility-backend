from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.feedback_model import Feedback_model
from app.schemas.feedback_schema import Feedback_request_schema, Feedback_response_schema
from app.core.database import get_db
from datetime import datetime
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi import Depends

db: Session = SessionLocal()

def send_feedback(title, message):
    feedback = Feedback_model(
            title=title,
            message=message,
            timestamp=datetime.now()
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    db.close()
    return Feedback_request_schema(title=title, message=message)

def get_paginated_feedbacks():
        return paginate(db, select(Feedback_model).order_by(Feedback_model.timestamp.desc()))