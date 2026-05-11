from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models.user_models import Users
from schemas.user_schema import RegistrationRequest
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from database.decorator import connection
from exceptions.user_exceptions import UserAlreadyExistsException, UserNotConfirmed
from utils.hashed import get_password_hash
import random

class UserLogic:

    def _get_user_code(name: str):
        """
        Хз какой код генерить. Из имени словно говно. Мб прост набор всего
        по типу #D3IOP2
        или хз
        """
        ...


    @connection()
    async def registeration_user(user: RegistrationRequest, session: AsyncSession):
        stmt = select(Users).where(Users.mail == user.mail)
        result = await session.execute(stmt)
        exist_user = result.scalar_one_or_none
        if exist_user:
            if exist_user.account_confirmed:
                raise UserAlreadyExistsException
            raise UserNotConfirmed

        hashed = get_password_hash(user.password)
        code = get_user_code()
        new_user = Users(
            name=user.name,
            mail=user.mail,
            password=hashed,
            nickname=user.nickname,
            code=code,
            account_confirmed=False,
            is_banned=False
        )
        session.add(new_user)
        await session.commit()
