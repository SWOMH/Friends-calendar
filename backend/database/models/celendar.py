from enum import Enum
from typing import Optional
from sqlalchemy import Boolean, String, Integer, Date, Time, Index, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base
from database.types import intpk
from datetime import date, time, datetime

class EventType(Enum):
    DAY_OFF = 'day_off' # Выходной
    WORKING_DAY = 'working_day' # Рабочий день
    BUSY = "busy" # Занят
    MY_OWN_PLANS= 'my_own_plans' # Свои планы
    FREE = 'free' # Свободен
    PLAY = 'play' # Играть
    MEETING = 'meeting' # Встреча
    TRIP = 'trip' # Поездка
    OTHER_EVENT = 'other_event' # Событие какое-нибудь. Тут по идее уже и будут предлогать куда попыздить

class Accuracy(Enum):
    DEFINITELY = 'definitely' # Точно 
    PLANNING_TO = 'planning_to' # Планирую
    MIGHT_GO = 'might_go' # Возможно, пойду
    DEFINITELY_NOT = 'definitely_not' # Точно не пойду

class CelendarEvent(Base):
    __tablename__ = "celendar_event"
    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.user.id"))
    type: Mapped[EventType]
    event_name: Mapped[Optional[str]] = mapped_column(String(56), nullable=True, comment='Название события')
    event_desctiption: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment='Описание события')
    planning: Mapped[Optional[Accuracy]] # А вот это хз надо ли (тип чел может планировать выставляя это, но хз)
    event_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    user = relationship("Users", back_populates="celendar")
    confirm = relationship("EventConfirmends", back_populates="event")
    comment = relationship("Comments", back_populates="event")

class Comments(Base):
    __tablename__ = 'comments_event'
    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.users.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.celendar_event.id"), nullable=False)
    comment: Mapped[str] = mapped_column(String(256))
    time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())

    user = relationship("Users", back_populates="comment")
    event = relationship("CelendarEvent", back_populates="comment")

class EventConfirmends(Base):
    __tablename__ = 'event_confirmends'
    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.users.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.celendar_event.id"), nullable=False)
    confirm_type: Mapped[Accuracy]

    user = relationship("Users", back_populates="confirmend")
    event = relationship("CelendarEvent", back_populates="confirm")
