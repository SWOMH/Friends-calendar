from fastapi import APIRouter
from schemas.user_schema import RegistrationRequest, UserResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["Регистрация и пользователь"])


@router.post('/', response_model=bool)
async def registration(user_info: RegistrationRequest) -> bool:
    ...
