from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.auth.auth_service import get_current_active_user
from app.main import app
from app.models.widget_config_model import WidgetConfig_model
from app.schemas.user_schema import User_schema

client = TestClient(app)


def override_get_current_user():
    """Mock user for testing authenticated endpoints"""
    return User_schema(
        id=1,
        username="testuser",
        email="test@example.com",
        is_active=True
    )


def test_get_config_success(monkeypatch):
    """Test successfully retrieving widget configuration"""
    def mock_get_widget_config(db):
        config = Mock(spec=WidgetConfig_model)
        config.id = 1
        config.version = "1.0.0"
        config.config_json = {
            "features": {
                "language_selector": {"enabled": True},
                "accessibility_profiles": {"enabled": True},
                "widget_controls": {
                    "contrast": {"enabled": True},
                    "reader": {"enabled": True},
                    "font_size": {"enabled": True},
                    "font_family": {"enabled": True},
                    "line_height": {"enabled": True},
                    "letter_spacing": {"enabled": True},
                    "disable_animations": {"enabled": True},
                    "hide_images": {"enabled": True},
                    "reading_guide": {"enabled": True},
                    "voice_navigation": {"enabled": True},
                    "highlight_links": {"enabled": True},
                    "saturation": {"enabled": True},
                    "color_filter": {"enabled": True}
                }
            }
        }
        config.deployment_status = "deployed"
        return config
    
    app.dependency_overrides[get_current_active_user] = override_get_current_user
    monkeypatch.setattr("app.api.admin_routes.get_widget_config", mock_get_widget_config)
    
    try:
        response = client.get("/admin/config")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["version"] == "1.0.0"
        assert data["deployment_status"] == "deployed"
        assert "features" in data["config"]
    finally:
        app.dependency_overrides.clear()


def test_get_config_not_found(monkeypatch):
    """Test handling when configuration doesn't exist"""
    from fastapi import HTTPException
    
    def mock_get_widget_config_not_found(db):
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    app.dependency_overrides[get_current_active_user] = override_get_current_user
    monkeypatch.setattr("app.api.admin_routes.get_widget_config", mock_get_widget_config_not_found)
    
    try:
        response = client.get("/admin/config")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Configuration not found"
    finally:
        app.dependency_overrides.clear()


def test_update_config_success(monkeypatch):
    """Test successfully updating widget configuration"""
    def mock_update_widget_config(db, config_json, version, deployment_status):
        config = Mock(spec=WidgetConfig_model)
        config.id = 1
        config.version = version
        config.config_json = config_json
        config.deployment_status = deployment_status
        return config
    
    async def mock_trigger_deployment():
        return {
            "status": "triggered",
            "environment": "production",
            "workflow": "pipeline_widget.yaml"
        }
    
    def mock_update_deployment_status(db, status):
        return Mock(deployment_status=status)
    
    app.dependency_overrides[get_current_active_user] = override_get_current_user
    monkeypatch.setattr("app.api.admin_routes.update_widget_config", mock_update_widget_config)
    monkeypatch.setattr("app.api.admin_routes.trigger_widget_deployment", mock_trigger_deployment)
    monkeypatch.setattr("app.api.admin_routes.update_deployment_status", mock_update_deployment_status)
    
    config_data = {
        "features": {
            "language_selector": {"enabled": True},
            "accessibility_profiles": {"enabled": True},
            "widget_controls": {
                "contrast": {"enabled": True},
                "reader": {"enabled": True},
                "font_size": {"enabled": True},
                "font_family": {"enabled": True},
                "line_height": {"enabled": True},
                "letter_spacing": {"enabled": True},
                "disable_animations": {"enabled": True},
                "hide_images": {"enabled": True},
                "reading_guide": {"enabled": True},
                "voice_navigation": {"enabled": True},
                "highlight_links": {"enabled": True},
                "saturation": {"enabled": True},
                "color_filter": {"enabled": True}
            }
        },
        "version": "1.1.0"
    }
    
    try:
        response = client.put("/admin/config", json=config_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Configuration updated and deployment triggered"
        assert data["deployment"]["status"] == "triggered"
        assert data["deployment"]["environment"] == "production"
    finally:
        app.dependency_overrides.clear()


def test_update_config_deployment_failure(monkeypatch):
    """Test handling deployment trigger failure"""
    def mock_update_widget_config(db, config_json, version, deployment_status):
        config = Mock(spec=WidgetConfig_model)
        config.id = 1
        config.version = version
        config.config_json = config_json
        config.deployment_status = deployment_status
        return config
    
    async def mock_trigger_deployment_failure():
        raise Exception("Failed to trigger workflow: Unauthorized")
    
    def mock_update_deployment_status(db, status):
        return Mock(deployment_status=status)
    
    app.dependency_overrides[get_current_active_user] = override_get_current_user
    monkeypatch.setattr("app.api.admin_routes.update_widget_config", mock_update_widget_config)
    monkeypatch.setattr("app.api.admin_routes.trigger_widget_deployment", mock_trigger_deployment_failure)
    monkeypatch.setattr("app.api.admin_routes.update_deployment_status", mock_update_deployment_status)
    
    config_data = {
        "features": {
            "language_selector": {"enabled": True},
            "accessibility_profiles": {"enabled": True},
            "widget_controls": {
                "contrast": {"enabled": True},
                "reader": {"enabled": True},
                "font_size": {"enabled": True},
                "font_family": {"enabled": True},
                "line_height": {"enabled": True},
                "letter_spacing": {"enabled": True},
                "disable_animations": {"enabled": True},
                "hide_images": {"enabled": True},
                "reading_guide": {"enabled": True},
                "voice_navigation": {"enabled": True},
                "highlight_links": {"enabled": True},
                "saturation": {"enabled": True},
                "color_filter": {"enabled": True}
            }
        },
        "version": "1.1.0"
    }
    
    try:
        response = client.put("/admin/config", json=config_data)
        
        assert response.status_code == 500
        assert "Failed to trigger deployment" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_get_deployment_status_success(monkeypatch):
    """Test successfully retrieving deployment status"""
    async def mock_get_deployment_status():
        return {
            "status": "completed",
            "conclusion": "success",
            "url": "https://github.com/owner/repo/actions/runs/123",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:10:00Z"
        }
    
    app.dependency_overrides[get_current_active_user] = override_get_current_user
    monkeypatch.setattr("app.api.admin_routes.get_deployment_status_from_github", mock_get_deployment_status)
    
    try:
        response = client.get("/admin/deployment/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["conclusion"] == "success"
        assert "github.com" in data["url"]
    finally:
        app.dependency_overrides.clear()


def test_get_deployment_status_no_runs(monkeypatch):
    """Test deployment status when no runs exist"""
    async def mock_get_deployment_status_unknown():
        return {"status": "unknown"}
    
    app.dependency_overrides[get_current_active_user] = override_get_current_user
    monkeypatch.setattr("app.api.admin_routes.get_deployment_status_from_github", mock_get_deployment_status_unknown)
    
    try:
        response = client.get("/admin/deployment/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unknown"
    finally:
        app.dependency_overrides.clear()


def test_update_config_without_version(monkeypatch):
    """Test updating config without specifying version (should default to 1.0.0)"""
    def mock_update_widget_config(db, config_json, version, deployment_status):
        config = Mock(spec=WidgetConfig_model)
        config.id = 1
        config.version = version
        config.config_json = config_json
        config.deployment_status = deployment_status
        return config
    
    async def mock_trigger_deployment():
        return {
            "status": "triggered",
            "environment": "production",
            "workflow": "pipeline_widget.yaml"
        }
    
    def mock_update_deployment_status(db, status):
        return Mock(deployment_status=status)
    
    app.dependency_overrides[get_current_active_user] = override_get_current_user
    monkeypatch.setattr("app.api.admin_routes.update_widget_config", mock_update_widget_config)
    monkeypatch.setattr("app.api.admin_routes.trigger_widget_deployment", mock_trigger_deployment)
    monkeypatch.setattr("app.api.admin_routes.update_deployment_status", mock_update_deployment_status)
    
    config_data = {
        "features": {
            "language_selector": {"enabled": True},
            "accessibility_profiles": {"enabled": True},
            "widget_controls": {
                "contrast": {"enabled": True},
                "reader": {"enabled": True},
                "font_size": {"enabled": True},
                "font_family": {"enabled": True},
                "line_height": {"enabled": True},
                "letter_spacing": {"enabled": True},
                "disable_animations": {"enabled": True},
                "hide_images": {"enabled": True},
                "reading_guide": {"enabled": True},
                "voice_navigation": {"enabled": True},
                "highlight_links": {"enabled": True},
                "saturation": {"enabled": True},
                "color_filter": {"enabled": True}
            }
        }
        # No version specified
    }
    
    try:
        response = client.put("/admin/config", json=config_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Configuration updated and deployment triggered"
    finally:
        app.dependency_overrides.clear()
