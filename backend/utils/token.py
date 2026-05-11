
from datetime import datetime, timedelta, UTC
from typing import Optional
import jwt
from config.constants import DEV_CONSTANT
from schemas.user_schema import TokenData

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or get_access_token_expire_delta())
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, DEV_CONSTANT.SECRET_KEY, algorithm=DEV_CONSTANT.ALGORITHM)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or get_refresh_token_expire_delta())
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, DEV_CONSTANT.SECRET_KEY, algorithm=DEV_CONSTANT.ALGORITHM)


def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    try:
        payload = jwt.decode(
            token, DEV_CONSTANT.SECRET_KEY, algorithms=[DEV_CONSTANT.ALGORITHM]
        )
        if payload.get("type") != token_type:
            return None
        sub = payload.get("sub")
        if sub is None:
            return None
        return TokenData(user_id=int(sub), email=payload.get("email"))
    except jwt.PyJWTError:
        return None


def get_access_token_expire_delta() -> timedelta:
    return timedelta(minutes=DEV_CONSTANT.ACCESS_TOKEN_EXPIRE_MINUTES)


def get_refresh_token_expire_delta() -> timedelta:
    return timedelta(days=DEV_CONSTANT.REFRESH_TOKEN_EXPIRE_DAYS)