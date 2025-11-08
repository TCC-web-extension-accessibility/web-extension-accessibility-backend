from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.auth_repository import AuthRepository
from sqlalchemy import select
from app.models.user_model import User_model

class AuthRepositoryImpl(AuthRepository):
    def __init__(self, session: Session):
        self.session = session
    def get_user_db(self, username: str) -> User_model | None:
        stmt = select(User_model).where(User_model.username == username)
        result = self.session.execute(stmt)
        return result.scalars().first()
    def update_password(self, username: str, new_password: str) -> None:
        user = self.get_user_db(username)
        if user is not None:
            user.hashed_password = new_password
            self.session.add(user)
            self.session.commit()
    def add_user(self, username: str, full_name: str, hashed_password: str, disabled: bool) -> None:
        if not self.get_user_db(username):
            user = User_model(
                username=username,
                full_name=full_name,
                hashed_password=hashed_password,
                disabled=disabled
            )
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user) 