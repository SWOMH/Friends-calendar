from database.models.user_models import Users
from fastapi import Depends, HTTPException, status
from exceptions.user_exceptions import UserBannedException, UserNotFoundExists
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from utils.token import verify_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Users:
    from database.logic.user_logic import DB_AUTH

    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(credentials.credentials, "access")
    if token_data is None:
        raise exc
    try:
        user = await DB_AUTH.user_get_by_token(token_data.user_id)
    except UserBannedException:
        raise exc
    except UserNotFoundExists:
        raise exc
    return user


async def get_current_active_user(
    current_user: Users = Depends(get_current_user),
) -> Users:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неактивный пользователь",
        )
    return current_user