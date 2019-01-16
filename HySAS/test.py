from multiprocessing import Process
import threading
import time
import os
import redis
import pickle
import logging

from HySAS.core.Functions import *


def __command_handler__(msg_command):
    print(msg_command)


redis_conn = get_vendor("DB").get_redis()
command_listener = redis_conn.pubsub()
channel_name = "dHydra.Command"
command_listener.subscribe([channel_name])
# for item in command_listener.listen():
#     if item["type"] == "message":
#         print(pickle.loads(item['data']))


from datetime import datetime

# status = dict()
# status["heart_beat"] = time.time()
# status["nickname"] = "zyyz"
# redis_key = "HySAS"
#
# redis_conn.hmset(redis_key + "Info", status)
# info = redis_conn.hgetall(redis_key + "Info")

worker_names = []
# path = os.path.join(os.path.split(os.path.realpath(__file__))[0]+"/Worker")
# worker_names.extend(os.listdir(path))
try:
    worker_names.extend(os.listdir(os.getcwd()+"/Worker"))
except FileNotFoundError as e:
    print("HySAS运行目录下没有Worker文件夹")

print(worker_names)


