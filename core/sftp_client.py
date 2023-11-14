# -*- coding:utf-8 -*
"""
@File  : sftp_client.py
@Author: DJW
@Date  : 2023-11-01 16:15
@Desc  : 连接以SFTP协议搭建的SFTP服务器客户端类
"""
import os
import sys
import time
import stat
from typing import List

import paramiko
from paramiko.ssh_exception import SSHException

from logging_config import sftp_client as logger


class SFTPClient:
    """
    sftp服务器客户端类
    :param hostname:连接到的ftp服务器ip
    :param username:用户名
    :param password:密码
    :param port:连接到的ftp服务器ip
    :param private_key_path:私钥文件绝对路径
    """

    def __init__(
            self,
            hostname: str,
            username: str,
            password: str,
            port: int = 22,
            keep_alive: int = 60,
            private_key_path: str = None
    ):
        self.keep_alive = keep_alive
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.private_key_path = private_key_path
        self.transport = None
        self.sftp = None
        self.system = sys.platform  # win32 / linux

    def connect(self):
        """开始连接SFTP服务器"""
        try:
            if self.sftp:
                self.sftp.close()
            if self.transport:
                self.transport.close()

            self.transport = paramiko.Transport((self.hostname, self.port))
            if self.password:
                self.transport.set_keepalive(self.keep_alive)
                self.transport.connect(username=self.username, password=self.password)
            else:
                private_key = paramiko.RSAKey.from_private_key_file(self.private_key_path)
                self.transport.set_keepalive(self.keep_alive)
                self.transport.connect(username=self.username, pkey=private_key)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            logger.info("连接SFTP服务器成功!!")
        except Exception as e:
            logger.error(f"{repr(e)}")
            logger.info(f"将在5秒后重连服务器...")
            time.sleep(5)
            self.reconnect()

    def reconnect(self):
        """重连SFTP服务器"""
        while True:
            if self.sftp:
                self.sftp.close()
            if self.transport:
                self.transport.close()
            try:
                self.transport = paramiko.Transport((self.hostname, self.port))
                if self.password:
                    self.transport.set_keepalive(self.keep_alive)
                    self.transport.connect(username=self.username, password=self.password)
                else:
                    private_key = paramiko.RSAKey.from_private_key_file(self.private_key_path)
                    self.transport.set_keepalive(self.keep_alive)
                    self.transport.connect(username=self.username, pkey=private_key)
                self.sftp = paramiko.SFTPClient.from_transport(self.transport)
                logger.info("连接SFTP服务器成功!")
                break
            except Exception as e:
                logger.error(f"{repr(e)}")
                logger.info(f"将在5秒后重连SFTP服务器...")
                time.sleep(5)

    def disconnect(self):
        """断开与SFTP服务器的连接"""
        if self.sftp:
            self.sftp.close()
            self.sftp = None
        if self.transport:
            self.transport.close()
            self.transport = None
        logger.info("已断开与SFTP服务器连接.")

    def upload_file(self, local_file: str, remote_file: str) -> bool:
        """
        上传单个文件（windows路径用"\"分隔，linux用"/"分隔）

        :param local_file:本地需要上传文件的绝对路径（例如：/path/file.txt）
        :param remote_file:远程存储文件的绝对路径（例如：/path/file.txt）
        :return:是否成功
        """
        try:
            self.sftp.put(local_file, remote_file)
            return True
        except SSHException as e:
            logger.error(f"{repr(e)}")
            self.reconnect()
        except Exception as e:
            logger.error(f"{repr(e)}")
            return False

    def upload_files(self, local_dir: str, remote_dir: str) -> bool:
        """
        批量上传文件（windows路径用"\"分隔，linux用"/"分隔）

        :param local_dir:本地需要批量上传文件的文件夹绝对路径（例如：/path/file）
        :param remote_dir:远程存储文件的文件夹绝对路径（例如：/path/file）
        :return:是否成功
        """
        try:
            for file in os.listdir(local_dir):
                local_path = os.path.join(local_dir, file)
                remote_path = os.path.join(remote_dir, file)
                # 根据传入的远程路径判断是否需要修改路径以契合远程服务器使用的系统
                remote_path = self.format_remote_path(remote_path)
                self.sftp.put(local_path, remote_path)
            return True
        except SSHException as e:
            logger.error(f"{repr(e)}")
            self.reconnect()
        except Exception as e:
            logger.error(f"{repr(e)}")
            return False

    def download_file(self, remote_file: str, local_file: str) -> bool:
        """
        下载单个文件（windows路径用"\"分隔，linux用"/"分隔）

        :param remote_file:远程需要下载文件的绝对路径（例如：/path/file.txt）
        :param local_file:本地需要保存文件的绝对路径（例如：/path/file.txt）
        :return:是否成功
        """
        try:
            self.sftp.get(remote_file, local_file)
            return True
        except SSHException as e:
            logger.error(f"{repr(e)}")
            self.reconnect()
        except Exception as e:
            logger.error(f"{repr(e)}")
            return False

    def download_files(self, remote_dir: str, local_dir: str) -> bool:
        """
        批量下载文件（windows路径用"\"分隔，linux用"/"分隔）

        :param remote_dir:远程需要批量下载文件的文件夹绝对路径（例如：/path/file）
        :param local_dir:本地需要保存文件的文件夹绝对路径（例如：/path/file）
        :return:是否成功
        """
        try:
            for file in self.sftp.listdir(remote_dir):
                remote_path = os.path.join(remote_dir, file)
                local_path = os.path.join(local_dir, file)
                # 根据传入的远程路径判断是否需要修改路径以契合远程服务器使用的系统
                remote_path = self.format_remote_path(remote_path)
                self.sftp.get(remote_path, local_path)
            return True
        except SSHException as e:
            logger.error(f"{repr(e)}")
            self.reconnect()
        except Exception as e:
            logger.error(f"{repr(e)}")
            return False

    def compare_files(self, local_file: str, remote_file: str) -> str:
        """
        比较本地文件和远程文件是否一样
        通过比较文件大小确定是否是同一个文件

        :param local_file:本地文件的绝对路径（例如：/path/file.txt）
        :param remote_file:远程文件的绝对路径（例如：/path/file.txt）
        :return: 本地等于远端:"="、本地大于远端:">"、本地小于远端:"<"、错误:""
        """
        try:
            # 获取本地文件的大小
            local_size = os.path.getsize(local_file)
            # 获取远程文件的大小
            remote_attr = self.sftp.stat(remote_file)
            remote_size = remote_attr.st_size
            if local_size == remote_size:
                return "="
            elif local_size > remote_size:
                return ">"
            elif local_size < remote_size:
                return "<"
            else:
                return ""
        except SSHException as e:
            logger.error(f"{repr(e)}")
            self.reconnect()
        except Exception as e:
            logger.error(f"{repr(e)}")
            return ""

    def delete_local_file(self, local_file: str) -> bool:
        """
        删除本地文件

        :param local_file:本地文件的绝对路径（例如：/path/file.txt）
        :return:是否删除成功
        """
        try:
            os.remove(local_file)
            return True
        except SSHException as e:
            logger.error(f"{repr(e)}")
            self.reconnect()
        except Exception as e:
            logger.error(f"{repr(e)}")
            return False

    def delete_remote_file(self, remote_file: str) -> bool:
        """
        删除远程文件

        :param remote_file:远程文件的绝对路径（例如：/path/file.txt）
        :return:是否删除成功
        """
        try:
            self.sftp.remove(remote_file)
            return True
        except SSHException as e:
            logger.error(f"{repr(e)}")
            self.reconnect()
        except Exception as e:
            logger.error(f"{e} [ {remote_file} ]")
            return False

    def check_local_file_exists(self, local_file: str) -> bool:
        """
        判断本地是否存在想要找的文件

        :param local_file:文件的绝对路径（例如：/path/file.txt）
        :return:是否存在
        """
        try:
            with open(local_file, 'r') as f:
                return True
        except SSHException as e:
            logger.error(f"{repr(e)}")
            self.reconnect()
        except IOError:
            return False

    def check_remote_file_exists(self, remote_file: str) -> bool:
        """
        判断远程SFTP服务器是否存在想要找的文件

        :param remote_file:文件的绝对路径（例如：/path/file.txt）
        :return:是否存在
        """
        try:
            self.sftp.stat(remote_file)
            return True
        except SSHException as e:
            logger.error(f"{repr(e)}")
            self.reconnect()
        except IOError:
            return False

    def check_remote_path_exists(self, remote_path: str) -> bool:
        """
        判断远程SFTP服务器下的目标路径是否存在

        :param remote_path:远程目标绝对路径（例如：/path/file）
        :return:是否存在
        """
        # 查看远程目标路径是否存在
        try:
            self.sftp.stat(remote_path)
            return True
        except SSHException as e:
            logger.error(f"{repr(e)}")
            self.reconnect()
        except IOError:
            return False

    def make_remote_dir(self, remote_path) -> bool:
        """
        创建远程文件夹

        :param remote_path:远程要创建文件夹的绝对路径（例如：/path/file）
        :return:是否创建成功
        """
        try:
            self.sftp.stat(remote_path)
            return False
        except SSHException as e:
            logger.error(f"{repr(e)}")
            self.reconnect()
        except FileNotFoundError:
            self.sftp.mkdir(remote_path)
            return True

    def get_remote_file_list(self, remote_path) -> List:
        """
        递归获取远程SFTP服务器目标路径及子目录下所有文件列表

        :param remote_path: 远程目标绝对路径
        :return: 该路径下所有文件及子目录所有文件的总列表，若没有文件则为空列表
        """
        try:
            file_list = []
            # 检查远程目标路径是否存在
            if self.check_remote_path_exists(remote_path):
                for item in self.sftp.listdir_attr(remote_path):
                    if stat.S_ISDIR(item.st_mode):
                        path = os.path.join(remote_path, item.filename)
                        path = self.format_remote_path(path)
                        # 如果是子目录，则递归调用扫描子目录下的文件，加入列表
                        files = self.get_remote_file_list(path)
                        file_list += files
                    else:
                        # 如果是文件，则加入列表
                        file_list.append(item.filename)
            return file_list
        except SSHException as e:
            logger.error(f"{repr(e)}")
            self.reconnect()
        except Exception as e:
            logger.error(f"{repr(e)}")
            return []

    def get_remote_all_file(self, remote_path) -> dict:
        """
        递归获取远程SFTP服务器目标路径下的所有文件夹和文件

        :param remote_path: 远程目标绝对路径
        :return:该路径下的所有文件夹及文件
        """
        try:
            file_dict = {}
            # 检查远程目标路径是否存在
            if self.check_remote_path_exists(remote_path):
                for item in self.sftp.listdir_attr(remote_path):
                    if stat.S_ISDIR(item.st_mode):
                        path = os.path.join(remote_path, item.filename)
                        path = self.format_remote_path(path)
                        # 如果是子目录，则递归调用扫描子目录下的文件，加入列表
                        files = self.get_remote_all_file(path)
                        file_dict[item.filename] = {"type": "dir", "files": files}
                    else:
                        # 如果是文件，则加入列表
                        file_dict[item.filename] = {"type": "file"}
            return file_dict
        except SSHException as e:
            logger.error(f"{repr(e)}")
            self.reconnect()
        except Exception as e:
            logger.error(f"{repr(e)}")
            return {}

    def format_remote_path(self, path) -> str:
        """
        根据传入的远程路径判断是否需要修改路径以契合远程服务器使用的系统

        :param path:路径
        :return:格式化后的路径
        """
        return_path = ""
        if "/" in path and self.system == "win32":
            return_path = path.replace("\\", "/")
        elif "\\" in path and self.system == "linux":
            return_path = path.replace("/", "\\")
        return return_path


if __name__ == '__main__':
    pass
    # sftp_client = SFTPClient(
    #     "192.168.1.68",
    #     "sencott",
    #     "sea12345"
    # )
    # sftp_client.connect()
    # sftp_client.disconnect()
