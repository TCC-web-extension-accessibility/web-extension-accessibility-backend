from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter
from app.schemas.auth import Token
from app.schemas.user_schema import User_schema
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth.auth_service import get_current_active_user, authenticate_user
from app.auth.jwt_handler import create_access_token
from sqlalchemy.orm import Session
from app.core.database import get_db

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
