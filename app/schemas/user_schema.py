from pydantic import BaseModel

class User_schema(BaseModel):
    username: str
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User_schema):
    hashed_password: str