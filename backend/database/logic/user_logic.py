from os import name
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user_models import Token, Users
from schemas.user_schema import RegistrationRequest, TokenResponse, UserLoginData
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from database.decorator import connection
from exceptions.user_exceptions import UserAlreadyExistsException, UserBannedException, UserNotConfirmed, UserNotFoundExists, \
    UserInvalidEmailOrPasswordException, UserTokenNotFoundException
from utils.hashed import get_password_hash, verify_password
import random
import string

class UserLogic:

    def _get_user_code(self, length: int = 5):
        """
        Похрен, буду рандом генерить
        """
        characters = string.ascii_uppercase + string.digits        
        code = f"#{''.join(random.choices(characters, k=length))}"
        return code


    @connection()
    async def registeration_user(self, user: RegistrationRequest, session: AsyncSession):
        stmt = select(Users).where(Users.mail == user.mail)
        result = await session.execute(stmt)
        exist_user = result.scalar_one_or_none()
        if exist_user:
            if exist_user.account_confirmed:
                raise UserAlreadyExistsException
            raise UserNotConfirmed

        hashed = get_password_hash(user.password)
        code = self._get_user_code()
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

    @connection()
    async def confirm_account(self, user_id: int, session: AsyncSession) -> bool:
        stmt = select(Users).where(Users.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundExists
        if user.account_confirmed:
            raise UserAlreadyExistsException
        user.account_confirmed = True
        session.add(user)
        await session.commit()

    @connection()
    async def login_user(self, login: str, password: str, session: AsyncSession) -> Users:
        stmt = select(Users).where(Users.login == login)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundExists
        if not verify_password(password, user.password):
            raise UserInvalidEmailOrPasswordException
        if not user.account_confirmed:
            raise UserNotConfirmed
        return user

    @connection()
    async def save_token(self, user_id: int, access_token: str, refresh_token: str, session: AsyncSession) -> None:        
        old = await session.execute(select(Token).where(Token.user_id == user_id))
        for t in old.scalars().all():
            await session.delete(t)
        session.add(
            Token(user_id=user_id, token=access_token, refresh_token=refresh_token)
        )
        await session.commit()

    @connection()
    async def user_verification_by_token(
        self, token_user_id: int, refresh_token: str, session: AsyncSession
    ) -> Users:
        stmt = select(Token).where(
            Token.user_id == token_user_id,
            Token.refresh_token == refresh_token,
        )
        result = await session.execute(stmt)
        db_token = result.scalar_one_or_none()
        if not db_token:
            raise UserTokenNotFoundException
        stmt = select(Users).where(Users.id == token_user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundExists
        if user.is_banned:
            raise UserBannedException
        return user

DB_AUTH = UserLogic()