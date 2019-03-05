"""
数据处理函数
"""
from core.Worker import Worker

class Process(Worker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
