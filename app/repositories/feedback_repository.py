from abc import ABC, abstractmethod
from app.models.feedback_model import Feedback_model

class FeedbackRepository(ABC):
    @abstractmethod
    def add(self, feedback: Feedback_model) -> None:
        pass
    @abstractmethod
    def get_paginated(self):
        pass