from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.feedback_schema import Feedback_response_schema
from sqlalchemy import select
from app.models.feedback_model import Feedback_model
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import Annotated
from fastapi import Depends
from app.core.database import SessionLocal

class FeedbackRepositoryImpl(FeedbackRepository):
    def __init__(self, session: Session):
        self.session = session
    def add(self, feedback: Feedback_model) -> None:
        self.session.add(feedback)
        self.session.commit()
    def get_paginated(self):
        query = select(Feedback_model).order_by(Feedback_model.timestamp.desc())
        return paginate(self.session, query)