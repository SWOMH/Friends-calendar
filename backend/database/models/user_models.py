from typing import Optional
from sqlalchemy import Boolean, BooleanClauseList, ForeignKey, String, Integer, BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base
from database.types import intpk

# Короче делаю пока под отдельный сайт, но мб переобуюсь и сделаю под телегу/вк
class Users(Base):
    __tablename__ = "users"
    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(156))
    mail: Mapped[str] = mapped_column(String(300), nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    nickname: Mapped[str] = mapped_column(String(100), comment="Ник") # Хз создавать его автоматом или дать возможность придумывать самим
    code: Mapped[Optional[str]] = mapped_column(String(6), comment="Код для добавления в друзья", nullable=True) # На всякий случай буду код создавать
    account_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

    tokens = relationship("Token", back_populates="user")
    friends = relationship("Friends", back_populates="user")
    celendar = relationship("CelendarEvent", back_populates="user")
    comment = relationship("Comments", back_populates="user")
    confirmend = relationship("EventConfirmends", back_populates="user")

    __table_args__ = (
        Index("ix_users_account_name", "name"),
        Index("ix_users_account_nick", "nickname"),
        Index("ix_users_account_code", "code"),
        Index("ix_users_account_confirmed", "account_confirmed"),
        Index("ix_users_is_banned", "is_banned"),
        {'schema': 'public'}
    )


class Token(Base):
    __tablename__ = "tokens"
    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str]
    refresh_token: Mapped[Optional[str]] = mapped_column(nullable=True)
    user = relationship("Users", back_populates="tokens")


class Friends(Base):
    __tablename__ = "friends"
    user_id_main: Mapped[int] = mapped_column(Integer, ForeignKey("public.users.id"), nullable=False, comment="Сам пользователь")
    user_id_friend: Mapped[int] = mapped_column(Integer, ForeignKey("public.users.id"), nullable=False, comment="Друг/заявка в друзья/удаленный друг")
    is_friend: Mapped[bool] = mapped_column(Boolean, default=False)
    is_request: Mapped[bool] = mapped_column(Boolean, default=True, comment="Запрос в друзья")
    
    user = relationship("Users", back_populates="friends")