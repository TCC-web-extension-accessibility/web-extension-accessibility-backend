from sqlalchemy.orm import Session

from app.auth.jwt_handler import get_password_hash
from app.core.database import SessionLocal, engine
from app.models.feedback_model import Base as Base_feedback
from app.models.user_model import Base as Base_user
from app.models.user_model import User_model
from app.models.widget_config_model import Base as Base_widget_config
from app.models.widget_config_model import WidgetConfig_model


def create_tables():
    Base_user.metadata.create_all(bind=engine)
    Base_feedback.metadata.create_all(bind=engine)
    Base_widget_config.metadata.create_all(bind=engine)

def seed_initial_data():
    db: Session = SessionLocal()
    
    # Seed admin user
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
    
    # Seed widget configuration
    if not db.query(WidgetConfig_model).first():
        default_config = {
            "features": {
                "language_selector": {
                    "enabled": True
                },
                "accessibility_profiles": {
                    "enabled": True
                },
                "widget_controls": {
                    "contrast": {
                        "enabled": True
                    },
                    "reader": {
                        "enabled": False
                    },
                    "font_size": {
                        "enabled": True
                    },
                    "font_family": {
                        "enabled": True
                    },
                    "line_height": {
                        "enabled": True
                    },
                    "letter_spacing": {
                        "enabled": True
                    },
                    "disable_animations": {
                        "enabled": True
                    },
                    "hide_images": {
                        "enabled": True
                    },
                    "reading_guide": {
                        "enabled": True
                    },
                    "voice_navigation": {
                        "enabled": True
                    },
                    "highlight_links": {
                        "enabled": True
                    },
                    "saturation": {
                        "enabled": True
                    },
                    "color_filter": {
                        "enabled": True
                    }
                }
            }
        }
        
        widget_config = WidgetConfig_model(
            version="1.0.0",
            config_json=default_config,
            deployment_status="deployed",
            deployment_url="https://accessibility-widget.pages.dev"
        )
        db.add(widget_config)
        db.commit()
        db.refresh(widget_config)
    
    db.close()
