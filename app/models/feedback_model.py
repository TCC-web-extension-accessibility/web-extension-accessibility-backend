from sqlalchemy import Column, String, Integer, DateTime
from app.core.database import Base

class Feedback_model(Base):
    __tablename__="feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)