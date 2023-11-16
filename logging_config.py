# -*- coding:utf-8 -*
"""
@File  : logging_config.py
@Author: lee
@Date  : 2022/7/13/0013 11:08:55
@Desc  :
"""
import logging
import os
import sys

LOGGING_CONFIG = dict(
    version=1,
    disable_existing_loggers=False,
    loggers={
        "master": {
            "level": "INFO",
            "handlers": ["console", "master"],
            "propagate": True,
            "qualname": "master.debug",
        },
        "local_upload_to_sftp": {
            "level": "INFO",
            "handlers": ["console", "local_upload_to_sftp"],
            "propagate": True,
            "qualname": "local_upload_to_sftp.debug",
        },
        "sftp_download_to_local": {
            "level": "INFO",
            "handlers": ["console", "sftp_download_to_local"],
            "propagate": True,
            "qualname": "sftp_download_to_local.debug",
        },
        "sftp_client": {
            "level": "INFO",
            "handlers": ["console", "sftp_client"],
            "propagate": True,
            "qualname": "sftp_client.debug",
        },
        "upload_log": {
            "level": "INFO",
            "handlers": ["console", "upload_log"],
            "propagate": True,
            "qualname": "upload_log.debug",
        },
        "download_log": {
            "level": "INFO",
            "handlers": ["console", "download_log"],
            "propagate": True,
            "qualname": "download_log.debug",
        },
    },
    handlers={
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": sys.stdout,
        },
        "master": {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/master/master.log',
            'maxBytes': 1024 * 1024,
            'delay': True,
            "formatter": "generic",
            "backupCount": 10,
            "encoding": "utf-8"
        },
        "local_upload_to_sftp": {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/local_upload_to_sftp/local_upload_to_sftp.log',
            'maxBytes': 1024 * 1024,
            'delay': True,
            "formatter": "generic",
            "backupCount": 10,
            "encoding": "utf-8"
        },
        "sftp_download_to_local": {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/sftp_download_to_local/sftp_download_to_local.log',
            'maxBytes': 1024 * 1024,
            'delay': True,
            "formatter": "generic",
            "backupCount": 10,
            "encoding": "utf-8"
        },
        "sftp_client": {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/sftp_client/sftp_client.log',
            'maxBytes': 1024 * 1024,
            'delay': True,
            "formatter": "generic",
            "backupCount": 10,
            "encoding": "utf-8"
        },
        "upload_log": {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/upload_log/upload_log.log',
            'maxBytes': 1024 * 1024,
            'delay': True,
            "formatter": "generic",
            "backupCount": 10,
            "encoding": "utf-8"
        },
        "download_log": {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/download_log/download_log.log',
            'maxBytes': 1024 * 1024,
            'delay': True,
            "formatter": "generic",
            "backupCount": 10,
            "encoding": "utf-8"
        },
    },
    formatters={
        # 自定义文件格式化器
        "generic": {
            "format": "%(asctime)s [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s",
            # "format": "%(asctime)s {%(process)d(%(thread)d)} [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S]",
            "class": "logging.Formatter",
        }
    }
)
master = logging.getLogger("master")
local_upload_to_sftp = logging.getLogger("local_upload_to_sftp")
sftp_download_to_local = logging.getLogger("sftp_download_to_local")

sftp_client = logging.getLogger("sftp_client")
upload_log = logging.getLogger("upload_log")
download_log = logging.getLogger("download_log")


def create_log_folder():
    """检查创建日志文件夹"""
    handlers = LOGGING_CONFIG['handlers']
    for handler in handlers:
        if handler != "console":
            item = handlers[handler]
            if 'filename' in item:
                filename = item['filename']
                dirname = os.path.dirname(filename)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                    print(f"新生成日志目录：{dirname}")
