from database.core import DatabaseCore
from config.constants import DEV_CONSTANT


class DataBaseMainConnect(DatabaseCore):
    def __init__(self):
        url_con = DEV_CONSTANT.DATABASE_URL
        super().__init__(str(url_con), create_tables=True)