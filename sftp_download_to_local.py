# -*- coding:utf-8 -*
"""
@File  : sftp_download_to_local.py
@Author: DJW
@Date  : 2023-11-13 10:13
@Desc  : 下载SFTP服务器远程目录及子目录下的所有规定格式文件，并将所有文件按照远程目录下的分类进行子目录划分
"""
import os
import time
import logging.config

from core.Enum import *
from core.sftp_client import SFTPClient
from logging_config import sftp_download_to_local as logger, create_log_folder, LOGGING_CONFIG


def download_file(sftp_c: SFTPClient, local_f: str, remote_f: str) -> bool:
    """
    下载、检查、删除文件

    :param sftp_c:sftp客户端类
    :param local_f:本地文件绝对路径
    :param remote_f:远端文件绝对路径
    :return: 成功：True、失败：False
    """
    try:
        # 下载文件
        download_r = sftp_c.download_file(remote_f, local_f)
        # 比较本地文件和远端文件
        compare_r = sftp_c.compare_files(local_f, remote_f)
        if download_r and compare_r == "=":
            logger.info(f"[ {remote_f} ] 下载成功!")
            # 若成功下载并且本地文件和远程文件一样则删除远程文件
            sftp_c.delete_remote_file(remote_f)
            logger.info(f"删除远程文件 [ {remote_f} ]")
            return True
        else:
            logger.error(f"[ {remote_f} ] 下载失败")
            return False
    except Exception as error:
        logger.error(f"{error}")
        return False


def traversal_file(sftp_c: SFTPClient, local_p: str, remote_p: str, remote_path_files: dict) -> bool:
    """
    递归遍历下载文件及文件夹内的文件

    :param sftp_c:sftp客户端类
    :param local_p:本地存储目录的绝对路径
    :param remote_p:远程文件目录的绝对路径
    :param remote_path_files:通过get_remote_all_file方法获取的路径下所有文件夹及文件字典
    :return: 成功：True、失败：False
    """
    try:
        for filename, info in remote_path_files.items():
            # 若当前为目录且目录下有文件，则递归下载该文件夹内的文件
            if info["type"] == "dir" and info["files"]:
                # 组合路径
                local_p_dir = os.path.join(local_p, filename)
                remote_p_dir = os.path.join(remote_p, filename)
                # 根据传入的远程路径判断是否需要修改路径以契合远程服务器使用的系统
                remote_p_dir = sftp_c.format_remote_path(remote_p_dir)
                # 若没有则创建本地文件夹
                if not os.path.exists(local_p_dir):
                    os.makedirs(local_p_dir)
                    logger.info(f"新生成存储目录：{local_p_dir}")
                # 遍历子目录
                logger.info(f"开始下载 [ {remote_p_dir} ]目录下的文件")
                traversal_file(sftp_c, local_p_dir, remote_p_dir, info["files"])
            elif info["type"] == "dir" and not info["files"]:
                # 若为空文件夹则跳过
                continue
            else:
                # 不是文件夹则开始检查文件并下载
                # 检查文件格式
                if not filename.endswith(DOWNLOAD_FILE_LAYOUT):
                    logger.error(f"[ {filename} ]文件格式有误，格式应为[ {DOWNLOAD_FILE_LAYOUT} ]")
                    continue
                local_file = os.path.join(local_p, filename)
                remote_file = os.path.join(remote_p, filename)
                # 根据传入的远程路径判断是否需要修改路径以契合远程服务器使用的系统
                remote_file = sftp_c.format_remote_path(remote_file)
                # 检查本地是否存在该文件
                if sftp_c.check_local_file_exists(local_file):
                    # 若本地存在该文件，则比较两个文件的大小
                    compare_res = sftp_c.compare_files(local_file, remote_file)
                    # 若本地文件小于远端文件，则删除本地文件进行重下，否则就删除远端文件
                    if compare_res == "<":
                        logger.info(f"开始重下 [ {remote_file} ]")
                        sftp_c.delete_local_file(local_file)
                        logger.info(f"删除本地文件 [ {local_file} ]")
                        download_file(sftp_c, local_file, remote_file)
                    else:
                        logger.info(f"[ {DOWNLOAD_LOCAL_PATH} ] 中已存在 [ {filename} ] 文件")
                        sftp_c.delete_remote_file(remote_file)
                        logger.info(f"删除远程文件 [ {remote_file} ]")
                        continue
                else:
                    download_file(sftp_c, local_file, remote_file)
        return True
    except Exception as error:
        logger.error(error)
        return False


def main():
    sftp_client = SFTPClient(HOSTNAME, USERNAME, PASSWORD)
    sftp_client.connect()
    while True:
        try:
            # 查询远程已有的压缩包
            all_files = sftp_client.get_remote_all_file(DOWNLOAD_REMOTE_PATH)
            file_list = sftp_client.get_remote_file_list(DOWNLOAD_REMOTE_PATH)
            if file_list:
                traversal_file(sftp_client, DOWNLOAD_LOCAL_PATH, DOWNLOAD_REMOTE_PATH, all_files)
                logger.info("======================================================================================")
                time.sleep(DOWNLOAD_TIME_INTERVAL)
            else:
                logger.warning("远程目录及子目录下无文件，10秒后再次扫描下载......")
                logger.info("======================================================================================")
                time.sleep(10)
        except Exception as e:
            logger.error(f"{e}")
            sftp_client.reconnect()


if __name__ == '__main__':
    # 创建日志目录
    create_log_folder()
    logging.config.dictConfig(LOGGING_CONFIG)  # logging config使能输出
    # 运行主程序
    main()
