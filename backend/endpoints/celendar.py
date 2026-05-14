from fastapi import APIRouter, Depends
from database.models.user_models import Users
from database.logic.celendar_logic import DB_SCHEDULE
from utils.user_depends import get_current_active_user

router = APIRouter(prefix="schedule", tags=["Календарь"])

@router.get('/')
async def get_all_schedule(user: Users = Depends(get_current_active_user)):
    """
    Получает все доступные евенты
    А хотя хз, там же и выходные, и сами евенты
    Наверн все сразу буду отдавать, смысл делить?
    там будет до 10-ти человек, скорее всего, но кешировать все равно будем
    Зря редис чтоль ставил
    """
    try:
        user_events_actual = DB_SCHEDULE.get_user_events()
    except:
        ...