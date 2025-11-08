from app.core.database import Base
from sqlalchemy import JSON, Column, Integer, String


class WidgetConfig_model(Base):
    __tablename__ = "widget_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, nullable=False)
    config_json = Column(JSON, nullable=False)
    deployment_status = Column(String, default="pending")
    deployment_url = Column(String, nullable=True)