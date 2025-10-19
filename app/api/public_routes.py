"""
Public API routes for CI/CD and external integrations
These endpoints use API key authentication instead of user tokens
"""
import os
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.widget_config_model import WidgetConfig_model
from app.schemas.widget_config_schema import WidgetConfigPublicResponse

router = APIRouter()


def verify_api_key(x_api_key: str = Header(...)) -> bool:
    """Verify API key for public endpoints"""
    expected_api_key = os.getenv("CONFIG_API_KEY")
    
    if not expected_api_key:
        raise HTTPException(
            status_code=500,
            detail="CONFIG_API_KEY not configured on server"
        )
    
    if x_api_key != expected_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return True


@router.get("/widget/config", response_model=WidgetConfigPublicResponse)
async def get_widget_config(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[bool, Depends(verify_api_key)]
):
    """
    Get widget configuration for CI/CD builds
    
    This endpoint is used by GitHub Actions to fetch the latest config
    Authentication: X-API-Key header
    """
    config = db.query(WidgetConfig_model).first()
    
    if not config:
        raise HTTPException(
            status_code=404,
            detail="Widget configuration not found"
        )
    
    return {
        "version": config.version,
        "features": config.config_json.get("features", {}),
    }


