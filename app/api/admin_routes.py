from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, MessageType
from starlette.responses import JSONResponse

from app.auth.auth_service import authenticate_user, get_current_active_user, get_user, update_password
from app.auth.jwt_handler import create_access_token, create_reset_password_token, decode_reset_password_token, get_password_hash
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, FRONTEND_FORGET_PASSWORD_URL, FRONTENTD_HOST, MAIL_CONF
from app.core.database import get_db
from app.schemas.auth import Token
from app.schemas.feedback_schema import Feedback_response_schema
from app.schemas.user_schema import User_schema
from app.schemas.widget_config_schema import (
    DeploymentStatusResponse,
    WidgetConfigAdminResponse,
    WidgetConfigUpdateRequest,
    WidgetConfigUpdateResponse,
)
from app.schemas.forget_password_schemas import ForgetPasswordRequest, SuccessMessage, ResetForgetPassword
from app.services.config_service import (
    get_deployment_status_from_github,
    get_widget_config,
    trigger_widget_deployment,
    update_deployment_status,
    update_widget_config,
)
from app.services.feedback_service import get_paginated_feedbacks


router = APIRouter()

@router.post("/login")
async def login_for_access_token(db: Annotated[Session, Depends(get_db)],form_data: Annotated[OAuth2PasswordRequestForm, Depends()],) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.get("/users/me/", response_model=User_schema)
async def read_users_me(current_user: Annotated[User_schema, Depends(get_current_active_user)],):
    return current_user

@router.get("/feedback", dependencies=[Depends(get_current_active_user)])
async def get_feedbacks(db: Annotated[Session, Depends(get_db)]) -> Page[Feedback_response_schema]:
    return get_paginated_feedbacks(db)

@router.post("/forget-password")
async def forget_password(background: BackgroundTasks, forget_schema: ForgetPasswordRequest, db: Annotated[Session, Depends(get_db)]):
    try:
        user = get_user(db, forget_schema.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid email address")
        token = create_reset_password_token(email=user.username)

        forget_url_link = f"{FRONTENTD_HOST}/{FRONTEND_FORGET_PASSWORD_URL}?email={user.username}&forgotPasswordCode={token}"

        email_body = {
            "company_name": "company name",
            "link_expiry_min": ACCESS_TOKEN_EXPIRE_MINUTES,
            "reset_link": forget_url_link
        }

        message = MessageSchema(
            subject="Intruções para reset de senha",
            recipients=[forget_schema.email],
            template_body=email_body,
            subtype=MessageType.html
        )

        template_name = "reset_password.html"

        fast_mail = FastMail(MAIL_CONF)
        background.add_task(fast_mail.send_message, message, template_name=template_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={"message": "Email de instruções para reset de senha enviado com sucesso.", "success":True, "status_code":status.HTTP_200_OK}, 
            )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail="Something Unexpected, Server Error")
    
@router.post("/reset-password", response_model=SuccessMessage)
async def reset_password(rfp: ResetForgetPassword, db:  Annotated[Session, Depends(get_db)]):
    try:
        info = decode_reset_password_token(token=rfp.secret_token)
        if info is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid Password Reset Payload or Reset Link Expired")
        if rfp.new_password != rfp.confirm_password:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="New password and confirm password are not same.")
        
        password_hash = get_password_hash(rfp.new_password)
        update_password(db, username=info, new_password=password_hash)
        return {'success': True, 'status_code': status.HTTP_200_OK, 'message': 'Password Reset Successfull!'}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail="Some thing unexpected happened!")

@router.get("/config", response_model=WidgetConfigAdminResponse)
async def get_config(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User_schema, Depends(get_current_active_user)]
):
    """Get widget configuration"""
    config = get_widget_config(db)
    
    return {
        "id": config.id,
        "version": config.version,
        "config": config.config_json,
        "deployment_status": config.deployment_status
    }

@router.put("/config", response_model=WidgetConfigUpdateResponse)
async def update_config(
    config_data: WidgetConfigUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User_schema, Depends(get_current_active_user)]
):
    """Update widget configuration and trigger deployment"""
    
    config_json = {"features": config_data.features.model_dump()}
    version = config_data.version or "1.0.0"
    
    config = update_widget_config(db, config_json, version, deployment_status="pending")
    
    # Trigger GitHub Actions workflow (workflow will fetch config from API)
    try:
        deployment_result = await trigger_widget_deployment()
        update_deployment_status(db, "deploying")
    except Exception as e:
        update_deployment_status(db, "failed")
        raise HTTPException(status_code=500, detail=f"Failed to trigger deployment: {str(e)}")
    
    return WidgetConfigUpdateResponse(
        message="Configuration updated and deployment triggered",
        config=config.config_json,
        deployment=deployment_result
    )

@router.get("/deployment/status", response_model=DeploymentStatusResponse)
async def get_deployment_status(
    current_user: Annotated[User_schema, Depends(get_current_active_user)]
):
    """Check deployment status from GitHub Actions"""
    deployment_data = await get_deployment_status_from_github()
    return DeploymentStatusResponse(**deployment_data)
