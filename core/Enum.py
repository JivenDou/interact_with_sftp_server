"""
@File  : Enum.py
@Author: DJW
@Date  : 2023-11-16 10:36
@Desc  : 通用枚举类 和 通用常量 定义
"""
from configparser import ConfigParser

config = ConfigParser()
config.read(r'./config.ini', encoding='utf-8')

# 测试使用的信息
# HOSTNAME = config['sftp_server']['hostname']
# USERNAME = config['sftp_server']['username']
# PASSWORD = config['sftp_server']['password']
# HOSTNAME = "192.168.1.68"
# USERNAME = "sencott"
# PASSWORD = "sea12345"

# 远程sftp服务器配置信息
HOSTNAME = "140.143.136.179"
USERNAME = "sftp_sencott"
PASSWORD = "7i)m@NnCG1wDr7i"
# 运行模式
RUN_MODE = int(config['mode']['run_mode'])
# 上传配置信息
UPLOAD_LOCAL_PATH = config['upload']['local_path']
UPLOAD_REMOTE_PATH = config['upload']['remote_path']
UPLOAD_FILE_LAYOUT = config['upload']['file_layout']
UPLOAD_TIME_INTERVAL = int(config['upload']['time_interval'])
# 下载配置信息
DOWNLOAD_LOCAL_PATH = config['download']['local_path']
DOWNLOAD_REMOTE_PATH = config['download']['remote_path']
DOWNLOAD_FILE_LAYOUT = config['download']['file_layout']
DOWNLOAD_TIME_INTERVAL = int(config['download']['time_interval'])
