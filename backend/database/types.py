from typing import Annotated
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import mapped_column

# Общий тип для первичного ключа
intpk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]
u_id = Annotated[int, mapped_column(Integer, ForeignKey("public.users.id"))]
