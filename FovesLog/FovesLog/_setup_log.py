import os
from pathlib import Path
import logging
import datetime

def setup_log(
        log_folder: Path=Path('./logs'),
        file_date_format: str='%Y_%m_%d',
        info_format: str='[%(asctime)s][%(levelname)s][%(name)s] %(message)s',
        save_to_file: bool=True,
        output_to_console: bool=True,
        console_level: int=logging.INFO,
):
    time = datetime.datetime.now().strftime(file_date_format)
    # 建立格式
    formatter = logging.Formatter(info_format)

    # 建立文件句柄
    if save_to_file:
        # 确认日志文件夹
        log_folder.mkdir(exist_ok=True)
        # 普通文件
        file_handle = logging.FileHandler(
            log_folder / f'{time}.log',
            encoding='UTF8',
        )
        file_handle.setLevel(logging.DEBUG)
        file_handle.setFormatter(formatter)

        # 最新一次
        latest_handle = logging.FileHandler(
            log_folder / f'latest.log',
            mode='w',
            encoding='UTF8'
        )

        latest_handle.setLevel(logging.DEBUG) 
        latest_handle.setFormatter(formatter)
    else:
        file_handle = None
        latest_handle = None
    
    # 尝试获取颜色
    try:
        from colorama import Fore, init  # pyright: ignore[reportMissingModuleSource]

        init(autoreset=True)  # 带颜色的设置
        
        class ColoredFormatter(logging.Formatter):
            COLOR_MAP = {
                logging.DEBUG: Fore.CYAN,
                logging.INFO: Fore.WHITE,
                logging.WARNING: Fore.YELLOW,
                logging.ERROR: Fore.RED,
                logging.CRITICAL: Fore.MAGENTA,
            }

            def format(self, record):
                msg = super().format(record)
                color = self.COLOR_MAP.get(record.levelno, Fore.WHITE)
                return f"{color}{msg}"

        colored_formatter = ColoredFormatter(info_format)
    except ImportError:
        colored_formatter = None

    # 建立终端句柄
    if output_to_console:
        console_handle = logging.StreamHandler()
        console_handle.setLevel(console_level)
        if colored_formatter is None:
            console_handle.setFormatter(formatter)
        else:
            console_handle.setFormatter(colored_formatter)
    else:
        console_handle = None
    
    # 配置根记录器
    root_logger = logging.getLogger()
    if file_handle:
        root_logger.addHandler(file_handle)
    if latest_handle:
        root_logger.addHandler(latest_handle)
    if console_handle:
        root_logger.addHandler(console_handle)
    root_logger.setLevel(logging.DEBUG)