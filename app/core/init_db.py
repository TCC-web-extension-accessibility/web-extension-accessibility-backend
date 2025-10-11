from app.core.database import engine, SessionLocal
from app.models.user_model import Base as Base_user
from app.models.feedback_model import Base as Base_feedback
from sqlalchemy.orm import Session
from app.models.user_model import User_model
from app.auth.jwt_handler import get_password_hash

def create_tables():
    Base_user.metadata.create_all(bind=engine)
    Base_feedback.metadata.create_all(bind=engine)

def seed_initial_data():
    db: Session = SessionLocal()
    if not db.query(User_model).filter(User_model.username=="admin@example.com").first():
        user = User_model(
            username="admin@example.com",
            full_name="Administrator",
            hashed_password=get_password_hash("senha123"),
            disabled=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)    
    db.close()
