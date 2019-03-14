"""
数据处理函数
"""
from core.Worker import Worker
from core.Functions import get_vendor
from core import util
import sys

class Process(Worker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def init_MySQLdb(self):
        self.raw_MySQL = get_vendor("DB").get_MySQLdb("raw_mysql.json")
        if self.raw_MySQL is False:
            self.logger.error("Cannot connect to raw_MySQLdb")
            return False
        self.event_MySQL = get_vendor("DB").get_MySQLdb("event_mysql.json")
        if self.event_MySQL is False:
            self.logger.error("Cannot connect to event_MySQLdb")
            return False

    def on_start(self):
        self.init_MySQLdb()

    def __producer__(self):   #拥有数据库句柄  通过 self.db调用
        """
        取数据
        :return: msg
        """
        msg = "data"
        self.__data_handler__(msg)
        pass

    def __data_handler__(self, msg):
        print(msg)
        print("======")
        pass
