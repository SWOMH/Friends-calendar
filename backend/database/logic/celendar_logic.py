from sqlalchemy.ext.asyncio import AsyncSession
from exceptions.schedule_exception import EventNotFoundException, ValueNotFoundException
from database.models.celendar import Accuracy, CelendarEvent, EventConfirmends
from sqlalchemy.orm import selectinload, session
from sqlalchemy import or_, select
from database.models.user_models import Friends, Users
from schemas.event_schema import AllEventsResponse, CalendarEventResponse
from database.decorator import connection
from exceptions.user_exceptions import UserNotPermissionException

class ScheduleLogic:

    @connection
    async def get_all_events(self, user_id: int, session: AsyncSession) -> AllEventsResponse:
        """
        Будет возвращать все события
        И свои, и друзей (мб говно идея, но для 4-х колек должно выдержать)
        Правда думаю это на малинке развернуть, а там и выходные тянуться будут
        """
        friends_subquery = (
            select(Friends.user_id_friend)
            .where(
                Friends.user_id_main == user_id,
                Friends.status == "accepted"
            )
        )
        query = (
            select(Users)
            .where(or_(
                Users.id == user_id,
                Users.id.in_(friends_subquery)
                ))
            .options(
                selectinload(Users.celendar)
            )
        )
        result = await session.scalars(query)
        users = result.all()

        return AllEventsResponse(users=users)

    @connection()
    async def confirm_event(self, user_id: int, event_id: int, confirm_type: str, session: AsyncSession):
        """
        Прост подтверждение. Хз может ли сам создатель подтверждать. Наверн да
        Наверн не буду сувать проверки на право подтверждать
        (будет возможность подтвердить приход на встречу не своих друзей)
        Ну а ибо нахуй мне тут куча проверок, фан проект от нечего делать
        """
        try:
            type_c = Accuracy(confirm_type)
        except ValueError:
            raise ValueNotFoundException
        event = (await session.scalar(
            select(EventConfirmends).where(
                EventConfirmends.event_id == event_id,
                EventConfirmends.user_id == user_id                 
                )
            ))
        if event:
            """Если подтверждение есть, то от создания нового
            подтверждения засейвит уникальный индекс
            ну а если пытается снова создать событие, то изменим статус
            Вообще надо бы это в отдельную штуку сделать
            """
            event.confirm_type = type_c
            session.add(event)
            await session.commit()
            return
        confirm = EventConfirmends(
            user_id=user_id,
            event_id=event_id,
            confirm_type=type_c
        )
        session.add(confirm)
        await session.commit()
        return

    @connection()
    async def delete_event(self, user_id: int, event_id: int) -> bool:
        event = (await session.scalar(
            select(CelendarEvent).where(
                CelendarEvent.id == event_id
                )
            ))
        if int(event.user_id) != int(user_id):
            raise UserNotPermissionException
        
    @connection()
    async def edit_event(self, user_id: int, event: CalendarEventResponse, session: AsyncSession):
        """
        Нужно запилить тип эвента сначала
        """
        event_db = (await session.scalar(CelendarEvent).where(CelendarEvent.id == event.id))
        if event_db is None:
            raise EventNotFoundException
        if event_db.user_id != user_id:
            raise UserNotPermissionException
        
        
        


DB_SCHEDULE = ScheduleLogic()
