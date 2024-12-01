import config as conf
import aiomysql
from aiomysql.connection import _ConnectionContextManager as ctxMan
from asyncio import AbstractEventLoop


class db():
    def __init__(self) -> None:
        self.host = conf.DB_HOST
        self.port = conf.DB_PORT
        self.user = conf.DB_USER
        self.__password = conf.DB_PASSWORD
        self.db_name = conf.DB_DB

    async def conn_create(self,
                          loop: AbstractEventLoop) -> ctxMan:
        connect = await aiomysql.connect(host=self.host,
                                         port=int(self.port),
                                         user=self.user,
                                         password=self.__password,
                                         db=self.db_name,
                                         loop=loop)
        return connect
