from app.core.database import engine, SessionLocal,get_db
from app.models.user_model import Base as Base_user
from app.models.feedback_model import Base as Base_feedback
from sqlalchemy.orm import Session
from app.models.user_model import User_model
from app.auth.jwt_handler import get_password_hash
from app.repositories.impl.auth_repository_impl import AuthRepositoryImpl

def create_tables():
    Base_user.metadata.create_all(bind=engine)
    Base_feedback.metadata.create_all(bind=engine)

def seed_initial_data():
    db: Session = SessionLocal()
    repository = AuthRepositoryImpl(db)
    repository.add_user(
        username="admin@example.com", 
        full_name="Administrator", 
        hashed_password=get_password_hash("senha123"),
        disabled=False)