from abc import ABC, abstractmethod
from app.models.user_model import User_model

class AuthRepository(ABC):
    @abstractmethod
    def get_user_db(self, username: str) -> User_model | None:
        pass
    def update_password(self, username: str, new_password: str) -> None:
        pass
    def add_user(self, username: str, full_name: str, hashed_password: str, disabled: bool):
        pass
