# FovesLog
包括一系列和日志相关的工具。

可使用 pip 安装或下载源码使用：
```BASH
pip install FovesLog
```

项目主页：
https://github.com/Foves7017/FovesLib

## setup_log
用于快速设置日志句柄，可以调节选项： 
`log_folder: Path=Path('./logs')`：保存日志文件的文件夹
`file_date_format: str='%Y_%m_%d'`：日志文件使用的时间格式
`info_format: str='[%(asctime)s][%(levelname)s][%(name)s] %(message)s'`：输出日志使用的消息格式
`save_to_file: bool=True`：是否保存日志文件
`output_to_console: bool=True`：是否将日志输出到终端
`console_level: int=logging.INFO`：将日志输出到终端时使用的等级

另外，如果安装了 `colorama` 库，在输出到终端时会自动设置彩色输出：

等级    |颜色
--------|----
DEBUG   |CYAN
INFO    |WHITE
WARNING |YELLOW
ERROR   |RED
CRITICAL|MAGENTA
## LoggedTask
用来快速建立耗时任务的日志。
使用时只需要使用上下文管理器创建实例：

```Python
with LoggedTask('等待'):
    time.sleep(5)
# [2026-06-19 17:23:41,182][INFO][任务-等待] 任务 等待 开始
# [2026-06-19 17:23:46,183][INFO][任务-等待] 任务 等待 完成，用时 5.00 秒
```

可以获取返回的 LoggedTask 对象，这个对象提供一个 checkpoint 方法。会使用创建任务时指定的等级输出一条调试消息，并输出到上一条输出的用时。

```Python
with LoggedTask('等待') as task:
    for i in range(5):
        task.checkpoint(f'{i=}')
        time.sleep(0.1)
# [2026-06-19 17:26:33,117][INFO][任务-等待] 任务 等待 开始
# [2026-06-19 17:26:33,118][INFO][任务-等待] i=0, 用时 0.00 秒
# [2026-06-19 17:26:33,218][INFO][任务-等待] i=1, 用时 0.10 秒
# [2026-06-19 17:26:33,319][INFO][任务-等待] i=2, 用时 0.10 秒
# [2026-06-19 17:26:33,420][INFO][任务-等待] i=3, 用时 0.10 秒
# [2026-06-19 17:26:33,520][INFO][任务-等待] i=4, 用时 0.10 秒
# [2026-06-19 17:26:33,621][INFO][任务-等待] 任务 等待 完成，用时 0.50 秒
```

可以通过 `logger` 指定输出所使用的 Logger，或通过 `level` 指定输出的等级

```Python
logger = logging.getLogger('TEST')
with LoggedTask('等待', level=logging.ERROR, logger=logger) as task:
    time.sleep(0.1)
# [2026-06-19 17:28:31,653][ERROR][TEST] 任务 等待 开始
# [2026-06-19 17:28:31,754][ERROR][TEST] 任务 等待 完成，用时 0.10 秒
```

可以通过指定 `time_precision` 的方式来指定显示的小数位数，默认为 2 

# 更新日志

v0.1.4
 - `LoggedTask.__init__` 添加了 `time_precision` 参数，可以用来指定小数位数

v0.1.3
 - 交换了 `LoggedTask.__init__` 中 `logger` 和 `level` 的位置，更加易于使用