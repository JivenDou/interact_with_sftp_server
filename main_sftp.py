"""
@File  : main_sftp.py
@Author: DJW
@Date  : 2023-11-16 10:33
@Desc  : 主进程
"""
import logging.config

from core.Enum import RUN_MODE
from logging_config import create_log_folder, LOGGING_CONFIG, main as logger
from local_upload_to_sftp import main as main_local_upload_to_sftp
from sftp_download_to_local import main as main_sftp_download_to_local

if __name__ == '__main__':
    # 创建日志目录
    create_log_folder()
    logging.config.dictConfig(LOGGING_CONFIG)  # logging config使能输出

    # 验证运行模式
    if RUN_MODE == 1:
        logger.info("运行模式：上传")
        main_local_upload_to_sftp()
    elif RUN_MODE == 2:
        logger.info("运行模式：下载")
        main_sftp_download_to_local()
    else:
        logger.info("没有启用任何进程，请在配置文件中设置运行模式")
