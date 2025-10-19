from typing import Any, Dict

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import (
    GITHUB_API_URL,
    GITHUB_REPO_NAME,
    GITHUB_REPO_OWNER,
    GITHUB_TOKEN,
)
from app.models.widget_config_model import WidgetConfig_model


def get_widget_config(db: Session) -> WidgetConfig_model:
    config = db.query(WidgetConfig_model).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


def update_widget_config(
    db: Session,
    config_json: Dict[str, Any],
    version: str,
    deployment_status: str = "pending"
) -> WidgetConfig_model:
    config = db.query(WidgetConfig_model).first()
    
    if not config:
        config = WidgetConfig_model(
            version=version,
            config_json=config_json,
            deployment_status=deployment_status
        )
        db.add(config)
    else:
        config.config_json = config_json
        config.version = version
        config.deployment_status = deployment_status
    
    db.commit()
    db.refresh(config)
    return config


def update_deployment_status(
    db: Session,
    status: str
) -> WidgetConfig_model:
    config = db.query(WidgetConfig_model).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    config.deployment_status = status
    db.commit()
    db.refresh(config)
    return config


async def trigger_widget_deployment() -> Dict[str, str]:
    
    workflow_dispatch_url = f"{GITHUB_API_URL}/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/actions/workflows/pipeline_widget.yaml/dispatches"
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    payload = {
        "ref": "main",
        "inputs": {
            "environment": "production"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(workflow_dispatch_url, headers=headers, json=payload)
        
        if response.status_code != 204:
            raise Exception(f"Failed to trigger workflow: {response.text}")
    
    return {
        "status": "triggered",
        "environment": "production",
        "workflow": "pipeline_widget.yaml"
    }


async def get_deployment_status_from_github() -> Dict[str, Any]:
    
    workflow_runs_url = f"{GITHUB_API_URL}/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/actions/workflows/pipeline_widget.yaml/runs"
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(workflow_runs_url, headers=headers, params={"per_page": 1})
        
        if response.status_code == 200:
            runs = response.json().get("workflow_runs", [])
            if runs:
                latest_run = runs[0]
                return {
                    "status": latest_run["status"],
                    "conclusion": latest_run.get("conclusion"),
                    "url": latest_run["html_url"],
                    "created_at": latest_run["created_at"],
                    "updated_at": latest_run["updated_at"]
                }
    
    return {"status": "unknown"}

