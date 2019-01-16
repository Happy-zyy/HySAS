from HySAS.console import logger
from HySAS.core.Functions import *
import time
import click
import pickle

__redis__ = get_vendor("DB").get_redis()
worker_dict = dict()


def __on_termination__(sig, frame):
    logger.info("The HySAS Server is about to terminate, pid:{}"
                .format(os.getpid())
                )
    sys.exit(0)


def bind_quit_signals():
    import signal
    shutdown_signals = [
        "SIGQUIT",  # quit 信号
        "SIGINT",  # 键盘信号
        "SIGHUP",  # nohup 命令
        "SIGTERM",  # kill 命令
    ]
    for s in shutdown_signals:
        if hasattr(signal, s):
            signal.signal(
                getattr(signal, s, None),
                __on_termination__
            )


def start_worker(worker_name, **kwargs):
    worker = get_worker_class(worker_name=worker_name, **kwargs)
    worker_dict[worker.nickname] = worker
    worker.start()


def terminate_worker(nickname=None, pid=None):
    import signal
    logger.info("{}".format(worker_dict))
    if pid is None:
        pid = get_pid_by_nickname(redis_cli=__redis__, nickname=nickname)
        os.kill(pid, signal.SIGTERM)
        i = 0
        while worker_dict[nickname]._popen is None and i < 30:
            time.sleep(0.1)
            i += 1
        worker_dict[nickname]._popen.wait(1)
        worker_dict.pop(nickname)


def get_workers_info(redis_cli=None, by="nickname", nickname=None, worker_name=None):
    if redis_cli is None:
        redis_cli = __redis__
    result = list()
    keys = list()
    if by == "nickname" and nickname is not None:
        keys = redis_cli.keys("HySAS.Worker.*." + nickname + ".Info")
    elif by == "worker_name" and worker_name is not None:
        keys = redis_cli.keys("HySAS.Worker." + worker_name + ".*.Info")
    for k in keys:
        result.append(redis_cli.hgetall(k))
    return result


def get_pid_by_nickname(redis_cli=None, nickname=None):
    if redis_cli is None:
        redis_cli = __redis__
    workers_info = get_workers_info(redis_cli=__redis__, nickname=nickname)
    if len(workers_info) == 1:
        return int(workers_info[0]["pid"])
    else:
        logger.warning("Worker is not Unique.")
        return 0




def __command_handler__(msg_command):
    # msg_command is a dict with the following structure:
    """
    msg_command = {
        "type"	:		"sys/user/data",
        "operation"	:	"operation_name",
        "kwargs"	:	"suppose that the operation is a function, we need to
                         pass some arguments",
        "token"		:	"the token is used to verify the authentication of the
                         operation"
        }
    """
    import sys
    try:
        msg_command = pickle.loads(msg_command)
        if not isinstance(msg_command, dict):
            return
    except Exception as e:
        traceback.print_exc()
        print("msg_command is not dict \n",e)
    if msg_command["type"] == "sys":
        if hasattr(
                sys.modules["HySAS.main"],
                msg_command["operation_name"]
        ):
            func = getattr(
                sys.modules["HySAS.main"],
                msg_command["operation_name"]
            )
            try:
                print(msg_command["kwargs"])
                result = func(**msg_command["kwargs"])
            except Exception as e:
                traceback.print_exc()
                logger.error(e)

    elif msg_command["type"] == "user":
        """
        用于接受前端用户数据
        """
        pass

    elif msg_command["type"] == "data":
        """
        用于接受关联分析时可能向外传输的交互信号
        """
        pass

# @click.command()
# @click.argument('what', nargs=-1)
def main(what=None):
    try:
        if what:
            if what[0] != "HySAS":
                print("Please input HySAS for starting")
                exit(0)
            else:
                print(
                    "Welcome to HySAS! Following is the awesome!!!"
                )
                logo = "Let`s go"
                print(logo)
                # open a thread for the Worker of Monitor
                start_worker(worker_name="Monitor",nickname="Monitor")
                logger.info("Monitor has started")

                # 开启Web
                if len(what) == 1:
                    # 没指定http端口，不开启Tornado
                    pass
                else:
                    port = int(what[1])
                    start_worker(worker_name="Web", nickname="Tornado")

            # 绑定退出信号
            bind_quit_signals()

            redis_conn = get_vendor("DB").get_redis()
            command_listener = redis_conn.pubsub()
            channel_name = "HySAS.Command"
            command_listener.subscribe([channel_name])

            # 数据关联 态势分析
            start_worker(worker_name="Process",nickname="Process")
            #print(worker_dict)
            for item in command_listener.listen():   #阻塞式
                if item["type"] == "message":
                    __command_handler__(item["data"])

        else:
            print("HySAS What?")
    except Exception as e:
        traceback.print_exc()
        logger.error("{}".format(e))
        print("Hail error?")


if __name__ == '__main__':
    main(what = ["HySAS"])