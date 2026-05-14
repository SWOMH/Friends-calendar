from datetime import date, time
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

class CalendarEventResponse(BaseModel):
    id: int
    user_id: int
    type: str
    event_name: Optional[str] = None
    event_desctiption: Optional[str] = None
    planning: Optional[str] = None
    event_date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserEventsResponse(BaseModel):
    id: int
    name: str
    nickname: str
    code: Optional[str] = None
    celendar: List[CalendarEventResponse]

    model_config = ConfigDict(from_attributes=True)


class AllEventsResponse(BaseModel):
    users: List[UserEventsResponse]

    model_config = ConfigDict(from_attributes=True)