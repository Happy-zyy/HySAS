import time
import os
import redis
import pickle
from HySAS.core.Functions import *

msg = {
        "type": "sys",
        "operation_name": "start_worker",
        "kwargs":"haha"
    }

print(pickle.dumps(msg))
__redis__ = get_vendor("DB").get_redis()
__redis__.publish("dHydra.Command", pickle.dumps(msg))