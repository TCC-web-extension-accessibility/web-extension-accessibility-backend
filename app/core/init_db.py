from core.database import engine, SessionLocal
from models.user_model import Base
from sqlalchemy.orm import Session
from models.user_model import User_model
from auth.jwt_handler import get_password_hash

def create_tables():
    Base.metadata.create_all(bind=engine)

def seed_initial_data():
    db: Session = SessionLocal()
    if not db.query(User_model).filter(User_model.username=="admin").first():
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
