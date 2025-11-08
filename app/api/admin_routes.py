from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter
from app.schemas.auth import Token
from app.schemas.user_schema import User_schema
from app.schemas.feedback_schema import Feedback_response_schema
from app.services.feedback_service import get_paginated_feedbacks
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, FRONTEND_FORGET_PASSWORD_URL, FRONTENTD_HOST, MAIL_CONF
from app.auth.auth_service import get_current_active_user, authenticate_user, get_user, update_password
from app.auth.jwt_handler import create_access_token, create_reset_password_token, decode_reset_password_token, get_password_hash
from sqlalchemy.orm import Session
from app.core.database import get_db
from fastapi_pagination import Page
from starlette.background import BackgroundTasks
from app.schemas.forget_password_schemas import ForgetPasswordRequest, SuccessMessage, ResetForgetPassword
from fastapi_mail import FastMail, MessageSchema, MessageType
from starlette.responses import JSONResponse

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

        forget_url_link = f"{FRONTENTD_HOST}/{FRONTEND_FORGET_PASSWORD_URL}/{token}"

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
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail="Some thing unexpected happened!")