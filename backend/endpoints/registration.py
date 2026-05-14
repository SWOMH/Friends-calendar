import random
from fastapi import APIRouter, Depends, HTTPException, status
from backend.database.models.user_models import Users
from backend.exceptions.user_exceptions import UserBannedException, UserInvalidEmailOrPasswordException, \
    UserMailNotCorrectException, UserNotConfirmed, UserNotFoundExists, UserTokenNotFoundException
from backend.utils.user_depends import get_current_active_user
from schemas.user_schema import RegistrationRequest, UserResponse, TokenResponse, RefreshTokenRequest
from database.logic.user_logic import DB_AUTH
from config.redis import redis_db
from sender.email import publish_email
from utils.token import get_access_token_expire_delta, create_access_token, create_refresh_token, verify_token

router = APIRouter(prefix="/auth", tags=["Регистрация и пользователь"])



@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: RegistrationRequest):
    try:
        new_user = await DB_AUTH.register_user(user_data)
    except UserMailNotCorrectException as e:
        raise HTTPException(status_code=400, detail=e.details)
    except UserNotConfirmed as e:
        raise HTTPException(status_code=406, detail=e.details)
    return {"user_id": new_user.id, "login": new_user.login}


@router.post("/resend_confirm_code", status_code=status.HTTP_200_OK)
async def resend_confirm_code(login: str) -> dict:
    """Отправить код подтверждения повторно (по логину). Возвращает user_id для ввода кода."""
    try:
        user = await DB_AUTH.get_user_by_email(login)
    except UserNotFoundExists:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.account_confirmed:
        raise HTTPException(status_code=400, detail="Аккаунт уже подтверждён")
    code = random.randint(1000, 9999)
    redis_db.set(f"{user.id}_code_confirmed", str(code), 300)
    to_email = user.email or user.login
    publish_email("confirm_registration", to_email, code=code)
    return {"user_id": user.id}


@router.post("/confirmed_message_email", status_code=status.HTTP_200_OK)
async def send_message_confirmed(user_id: int) -> dict:
    user = await DB_AUTH.get_user_by_id(user_id)
    code = random.randint(1000, 9999)
    await redis_db.set(f"{user_id}_code_confirmed", str(code), 300)
    to_email = user.email or user.login
    publish_email("confirm_registration", to_email, code=code)
    return {"message": "message send"}


@router.post("/code_acc", status_code=status.HTTP_200_OK)
async def message_confirmed(user_id: int, code: int) -> dict:
    raw = await redis_db.get(f"{user_id}_code_confirmed")
    print(f"Raw from Redis: {raw}")
    print(f"Received code: {code}")
    
    if raw is None:
        raise HTTPException(status_code=404, detail="Code not found or expired")
    
    if str(code) == raw.decode("utf-8"):
        await DB_AUTH.activate_user(user_id)
        return {"message": "Account activated"}
    
    raise HTTPException(status_code=400, detail="Code not matched")


@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserResponse) -> TokenResponse:
    try:
        user = await DB_AUTH.authenticate_user(login_data.email, login_data.password)
    except UserInvalidEmailOrPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.details,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except UserNotFoundExists as e:
        raise HTTPException(status_code=403, detail=e.details)
    except UserNotConfirmed as e:
        raise HTTPException(
            status_code=403,
            detail=getattr(e, "details", "Подтвердите аккаунт по коду из письма"),
        )

    access_token = create_access_token({
        "sub": str(user.id),
        "email": user.name,
    })
    refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email or user.login})
    await DB_AUTH.save_token(user.id, access_token, refresh_token)
    expires_in = int(get_access_token_expire_delta().total_seconds())
    return TokenResponse(
        token=access_token,
        refresh_token=refresh_token,
        # token_type="bearer",
        # expires_in=expires_in,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest) -> TokenResponse:
    token_data = verify_token(refresh_data.refresh_token, "refresh")
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный refresh токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user = await DB_AUTH.user_verification_by_token(
            token_data.user_id, refresh_data.refresh_token
        )
    except (UserTokenNotFoundException, UserNotFoundExists, UserBannedException) as e:
        raise HTTPException(status_code=401, detail=getattr(e, "details", "Unauthorized"))

    access_token = create_access_token({
        "sub": str(user.id),
        "email": user.name,
    })
    new_refresh = create_refresh_token({"sub": str(user.id), "email": user.email or user.login})
    await DB_AUTH.save_token(user.id, access_token, new_refresh)
    return TokenResponse(
        token=access_token,
        refresh_token=new_refresh,
    )


@router.post("/password_reset_mail_send", status_code=status.HTTP_200_OK)
async def password_reset_mail_send(email: str) -> dict:
    try:
        user = await DB_AUTH.get_user_by_email(email)
    except UserNotFoundExists as e:
        raise HTTPException(status_code=404, detail=e.details)
    code = random.randint(1000, 9999)
    redis_db.set(f"{user.id}_code_reset", str(code), 300)
    to_email = user.email or user.login
    publish_email("reset_password", to_email, code=code)
    return {"message": "Code sent"}


@router.post("/password_reset_confirm_code", status_code=status.HTTP_200_OK)
async def password_reset_confirm_code(email: str, code: int) -> dict:
    try:
        user = await DB_AUTH.get_user_by_email(email)
    except UserNotFoundExists as e:
        raise HTTPException(status_code=404, detail=e.details)
    raw = redis_db.get(f"{user.id}_code_reset")
    if raw and str(code) == raw.decode("utf-8"):
        redis_db.set(f"{user.id}_reset_password_permission", "1", 600)
        return {"message": "Password reset confirmed"}
    return {"message": "Code not matched"}


@router.post("/password_reset_confirm", status_code=status.HTTP_200_OK)
async def password_reset_confirm(email: str, new_password: str) -> dict:
    try:
        user = await DB_AUTH.get_user_by_email(email)
    except UserNotFoundExists as e:
        raise HTTPException(status_code=404, detail=e.details)
    if redis_db.get(f"{user.id}_reset_password_permission") is None:
        raise HTTPException(status_code=400, detail="Password reset not confirmed")
    await DB_AUTH.update_user_password(user.id, new_password)
    return {"message": "Password updated"}


@router.post("/logout")
async def logout_user(current_user: Users = Depends(get_current_active_user)) -> dict:    
    await DB_AUTH.logout_user(current_user.id)
    return {"message": "Успешный выход из системы"}
