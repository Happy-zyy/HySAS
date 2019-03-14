# HySAS简介
HySAS(Hydrogen Situation Awareness System )是一个安全态势感知系统的开发框架，用于实现多进程多数据源的实时计算。不管是在开发过程还是运行过程中，都拥有极高的并行性和扩展性。  
**特点**
+ 采用Redis作为消息队列，实现进程间通信
+ 每个Worker都可以被独立工作，必要时可以相互配合
+ 支持动态联编，灵活加载功能模块


# 运行环境
 - python 3.5以上 (开发环境windows 10, python 3.6)，**不对python2.7提供支持，多版本虚拟环境安装请参考安装HySAS文档**
 - Mysql 8.0.13
 - Redis X64 3.2

 # Quick Start
1.  Step 1:安装Redis（略）
2.  Step 2:安装Mysql（略）


# 目录介绍


# 核心对象

## main.py
主程序入口  
main程序订阅了`HySAS.Command`频道，通过向这个频道发送命令可以开启或关闭响应的服务  
`worker_dict` : 对象字典`worker_dict[worker_name.nickname]：worker对象`用于记录系统中正在运行的worker对象

## console.py
允许通过命令行的形式，以第三方的身份动态加载Worker对象。旨在解决如果主程序中有部分Worker died之后，无需重启主程序，便可重启部分Worker，保证数据流的畅通性。

**用命令行启动/关闭**
```
start Demo DemoName
```
这样做就会开启一个叫`DemoName`的`Demo`进程  
这里的`DemoName`是`nickname`，`nickname`是全局唯一的，可能有多个不同的进程都是Demo类，但是每个进程都有唯一的昵称。  
以Worker为例：
  >  - 自己订阅了自己的频道
  >  - 每秒向Redis中的`HySAS.Worker.Demo.DemoName.Pub`频道发送一个数字
  >  - 将自己订阅收到的内容打印到屏幕

> 原理：之所以可以这样做是因为运行了`pip install --editable .`，它在你当前环境下认识了start命令，它会调用HySAS.console下的start方法，这个方法向Redis中的"HySAS.Command"频道发送了一条指令，HySAS Server监听到此指令以后就会实例化Demo目录下的DemoName类对象

```
stop DemoName
```
> 运行stop DemoName后，我们会向"HySAS.Command"频道发送一条指令，由HySAS Server去执行这个关闭Demo的任务，会捕捉到终止信号，并且执行用户自定义的`__before_termination__`

## 1.Worker
Worker类是HySAS的任务处理单元的基类，其继承于`multiprocessing.Process`。用于并行处理各个子任务，其派生类包括`Monitor`、`Process`。  
###工作流程
`__init__（）`：初始化成员变量。比较重要的成员：`self.__data_feeder__ = set()`用于存储本Worker订阅的内容。  
`run（）`：  
`__on_start__()`：用于连接redis（所有Worker共同订阅了`HySAS`频道）、Mysql，并实例化logger
`on_start()`：自定义启动项，用于拓展接口  
`__is_unique__()`：首先检查是否已经有相同的进程被开启，通过worker启动的时间，每个worker会生产一个唯一的`token`    
`__thread_listen_command__`：监听命令线程（守护进程），订阅了`self.redis_key.Command`频道，其中`self.redis_key`由创建worker时传入的参数决定。  
`__thread_pub__`：生产者进程（按需开启）  
`__thread_sub__`：消费者进程（按需开启），获取了订阅`HySAS`频道的redis句柄，并实时接受数据进行处理  
`__command_handler__`：上述的数据处理函数   
`__heart_beat__()`：为该worker注册心跳包，用于检验该worker是否被多重开启、存活性等。通过在`self.redis_key.Info`频道发布自身状态信息 ，心跳包内容如下：
```python
status = dict()
#以下必带
status["heart_beat"] = time.time()
status["nickname"] = self.__nickname__
status["pid"] = self.pid
status["token"] = self.__token__
status["heart_beat_interval"] = self.__heart_beat_interval__
#以下选带
if self.__error_msg__:
    status["error_msg"] = self.__error_msg__
if self.__stop_info__:
    status["stop_info"] = self.__stop_info__
if self.__stop_info__:
    status["stop_time"] = self.__stop_time__
if self.__status__:
    status["status"] = self.__status__
if self.__threads__:
    status["threads"] = copy.deepcopy(self.__threads__)
if self.__data_feeder__:
    status["data_feeder"] = self.__data_feeder__
if self.__follower__:
    status["follower"] = self.__follower__
self.__redis__.hmset(self.redis_key + "Info", status)
```
## 2.Monitor
继承于Worker，主要用于派生WorkerManger对象监视各个Worker的运行状态

## 3.WorkerManger
WorkerManger继承于Vendor，由Woker类的派生类对象Monitor重写了`run（）`中由`__thread_pub__`调用的`__producer__`生产。  
### 工作流程
`__init__（）`：初始化成员变量，获取redis句柄。  
`update_workers（）`：更新Worker信息。从redis获取所有对象的心跳包，以`dict[workerName][nickName] ：心跳包`的字典格式存入`work_info`。如果发现当前时间间隔大于worker的`heart_beat_interval`，即心跳停止，则放出warning，并从redis中删除该Worker信息。
