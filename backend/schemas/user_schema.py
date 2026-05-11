from typing import Optional
from pydantic import BaseModel, field_validator, EmailStr

class RegistrationRequest(BaseModel):
    mail: EmailStr
    password: str
    name: str
    nickname: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if v.islower() or v.isupper() or v.isnumeric():
            raise ValueError("Пароль должен содержать буквы разного регистра и цифры")
        return v



class UserResponse(BaseModel):
    id: int
    name: str
    code: Optional[str]
    nickname: str
    is_banned: bool
    account_confirmed: bool

class TokenResponse(BaseModel):
    id: int
    token: str
    refresh_token: str
    

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
