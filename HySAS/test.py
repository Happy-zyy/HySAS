from multiprocessing import Process
import threading
import time
import os
import redis
import pickle

from HySAS.core.Functions import *


def __command_handler__(msg_command):
    print(msg_command)

#
# redis_conn = get_vendor("DB").get_redis()
# command_listener = redis_conn.pubsub()
# channel_name = "dHydra.Command"
# command_listener.subscribe([channel_name])
# for item in command_listener.listen():
#     if item["type"] == "message":
#         print(pickle.loads(item['data']))


e  = "fksbkbjbj kfn knfk nfdkj"
print("msg_command is not dict \n",e)


