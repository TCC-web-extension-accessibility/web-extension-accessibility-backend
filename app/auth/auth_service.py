from typing import Annotated
from fastapi import Depends,HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.auth.jwt_handler import decode_access_token, verify_password
from app.schemas.auth import TokenData
from jwt.exceptions import InvalidTokenError
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models.user_model import User_model

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_user(db: Session, username: str) -> User_model |  None:
    return db.query(User_model).filter(User_model.username == username).first()

def authenticate_user(db: Session, username: str, password: str) -> User_model | bool:
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = db.query(User_model).filter(User_model.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Annotated[User_model, Depends(get_current_user)],):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


