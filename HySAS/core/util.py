import logging
import os
import hashlib
import time
import json

def get_worker_names(logger=None):
    """
    根据文件夹名字返回所有可能的worker_name
    :return:
    """
    worker_names = []
    # path = os.path.split(os.path.realpath(__file__))[0][:-6]+"/Worker"
    # worker_names.extend(os.listdir(path))
    try:
        worker_names.extend(os.listdir(os.getcwd()+"/Worker"))
    except FileNotFoundError as e:
        if logger is None:
            print("HySAS运行目录下没有Worker文件夹")
        else:
            logger.warning("HySAS运行目录下没有Worker文件夹")

    return worker_names

def get_logger(
    logger_name="main",
    log_path="log",                     #
    console_log=True,                   # 屏幕打印日志开关，默认True
    console_log_level=logging.INFO,     # 屏幕打印日志的级别，默认为INFO
    critical_log=False,                 # critical单独写文件日志，默认关闭
    error_log=True,                     # error级别单独写文件日志，默认开启
    warning_log=False,                  # warning级别单独写日志，默认关闭
    info_log=True,                      # info级别单独写日志，默认开启
    debug_log=False,                    # debug级别日志，默认关闭
):
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    if log_path:
        # 补全文件夹
        if log_path[-1] != '/':
            log_path += '/'

    if not logger.handlers:
        # 屏幕日志打印设置
        if console_log:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.INFO)
            logger.addHandler(console_handler)

        if not os.path.exists(log_path + logger_name):
            os.makedirs(log_path + logger_name)
        # 打开下面的输出到文件
        if critical_log:
            log_handler = logging.FileHandler(
                log_path + logger_name + '/critical.log'
            )
            log_handler.setLevel(logging.CRITICAL)
            log_handler.setFormatter(formatter)
            logger.addHandler(log_handler)
        if error_log:
            log_handler = logging.FileHandler(
                log_path + logger_name + '/error.log'
            )
            log_handler.setLevel(logging.ERROR)
            log_handler.setFormatter(formatter)
            logger.addHandler(log_handler)
        if warning_log:
            log_handler = logging.FileHandler(
                log_path + logger_name + '/warning.log'
            )
            log_handler.setLevel(logging.WARNING)
            log_handler.setFormatter(formatter)
            logger.addHandler(log_handler)
        if info_log:
            log_handler = logging.FileHandler(
                log_path + logger_name + '/info.log'
            )
            log_handler.setLevel(logging.INFO)
            log_handler.setFormatter(formatter)
            logger.addHandler(log_handler)
        if debug_log:
            log_handler = logging.FileHandler(
                log_path + logger_name + '/debug.log'
            )
            log_handler.setLevel(logging.DEBUG)
            log_handler.setFormatter(formatter)
            logger.addHandler(log_handler)
    return logger


def generate_token():
    token = hashlib.sha1()
    token.update(str(time.time()).encode())
    token = token.hexdigest()
    return token

def read_config(file_path):
    # 读取配置
    try:
        f_config = open(file_path)
        cfg = json.load(f_config)
    except Exception as e:
        print("{}".format(e))
        cfg = dict()
        print(
            "未能正确加载{}，请检查路径，json文档格式，或者忽略此警告"
            .format(file_path)
        )
    return cfg
