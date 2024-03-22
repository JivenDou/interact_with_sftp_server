# -*- coding:utf-8 -*
"""
@File  : local_upload_to_sftp.py
@Author: DJW
@Date  : 2023-11-06 14:16
@Desc  : 将本地目录下的所有文件，以设定上传时间间隔进行单个文件依次上传至远程SFTP服务器中的目标目录
"""
import os
import time
import logging.config

from core.Enum import *
from core.sftp_client import SFTPClient
from logging_config import local_upload_to_sftp as logger, create_log_folder, LOGGING_CONFIG


def upload_file(sftp_c: SFTPClient, local_f: str, remote_f: str) -> bool:
    """
    上传、检查、删除文件

    :param sftp_c:sftp客户端类
    :param local_f:本地文件绝对路径
    :param remote_f:远端文件绝对路径
    :return: 成功：True、失败：False
    """
    try:
        # 上传文件
        upload_r = sftp_c.upload_file(local_f, remote_f)
        # 比较本地文件和远端文件
        compare_r = sftp_c.compare_files(local_f, remote_f)
        if upload_r and compare_r == "=":
            logger.info(f"[ {local_f} ] 上传成功!")
            # 若成功上传并且本地文件和远程文件一样则删除本地文件
            sftp_c.delete_local_file(local_f)
            logger.info(f"删除本地文件 [ {local_f} ]")
            return True
        else:
            logger.error(f"[ {local_f} ] 上传失败")
            return False
    except Exception as error:
        logger.error(f"{error}")
        return False


def traversal_file(sftp_c: SFTPClient, local_p: str, remote_p: str, local_path_files: dict) -> bool:
    """
        递归遍历上传文件及文件夹内的文件

        :param sftp_c:sftp客户端类
        :param local_p:本地文件目录的绝对路径
        :param remote_p:远程文件目录的绝对路径
        :param local_path_files:通过get_local_all_file方法获取的路径下所有文件夹及文件字典
        :return: 成功：True、失败：False
    """
    try:
        for filename, info in local_path_files.items():
            # 若当前为目录且目录下有文件，则递归上传该文件夹内的文件
            if info["type"] == "dir" and info["files"]:
                # 组合路径
                local_p_dir = os.path.join(local_p, filename)
                remote_p_dir = os.path.join(remote_p, filename)
                # 根据传入的远程路径判断是否需要修改路径以契合远程服务器使用的系统
                remote_p_dir = sftp_c.format_remote_path(remote_p_dir)
                # 若没有则创建远程文件夹
                if not sftp_c.check_remote_path_exists(remote_p_dir):
                    sftp_c.make_remote_dir(remote_p_dir)
                    logger.info(f"新生成远程存储目录：{remote_p_dir}")
                # 遍历子目录
                logger.info(f"开始上传 [ {local_p_dir} ]目录下的文件")
                traversal_file(sftp_c, local_p_dir, remote_p_dir, info["files"])
            # 若为空文件夹则跳过
            elif info["type"] == "dir" and not info["files"]:
                continue
            # 不是文件夹则开始检查文件并上传
            else:
                # 检查文件格式
                if not filename.endswith(UPLOAD_FILE_LAYOUT):
                    logger.error(f"[ {filename} ]文件格式有误，格式应为[ {UPLOAD_FILE_LAYOUT} ]")
                    continue
                local_file = os.path.join(local_p, filename)
                remote_file = os.path.join(remote_p, filename)
                # 根据传入的远程路径判断是否需要修改路径以契合远程服务器使用的系统
                remote_file = sftp_c.format_remote_path(remote_file)
                # 检查远端是否存在该文件
                if sftp_c.check_remote_file_exists(remote_file):
                    # 若远端存在该文件，则比较两个文件的大小
                    compare_res = sftp_c.compare_files(local_file, remote_file)
                    # 若本地文件大于远端文件，则删除远端文件进行重传，否则就删除本地文件
                    if compare_res == ">":
                        logger.info(f"开始重传 [ {local_file} ]")
                        upload_file(sftp_c, local_file, remote_file)
                    else:
                        logger.info(f"[ {UPLOAD_REMOTE_PATH} ] 中已存在 [ {filename} ] 文件")
                        sftp_c.delete_local_file(local_file)
                        logger.info(f"删除本地文件 [ {local_file} ]")
                        continue
                else:
                    upload_file(sftp_c, local_file, remote_file)
                logger.info(
                    f"--------------------------{UPLOAD_TIME_INTERVAL}秒后上传下一个文件--------------------------")
                time.sleep(UPLOAD_TIME_INTERVAL)
        return True
    except Exception as error:
        logger.error(error)
        return False


def main():
    sftp_client = SFTPClient(HOSTNAME, USERNAME, PASSWORD)
    sftp_client.connect()
    while True:
        try:
            # 查询本地已有的压缩包
            all_files = sftp_client.get_local_all_file(UPLOAD_LOCAL_PATH)
            # 检查远程目录是否存在
            path_res = sftp_client.check_remote_path_exists(UPLOAD_REMOTE_PATH)
            if len(all_files) != 0 and path_res:
                traversal_file(sftp_client, UPLOAD_LOCAL_PATH, UPLOAD_REMOTE_PATH, all_files)
                logger.warning(f"本次上传完成, {UPLOAD_TIME_INTERVAL / 2}秒后再次扫描上传......")
            elif not path_res:
                try:
                    # 创建远程文件夹
                    mkdir_res = sftp_client.make_remote_dir(UPLOAD_REMOTE_PATH)
                    if mkdir_res:
                        logger.info(f'[ {UPLOAD_REMOTE_PATH} ] 远程文件夹创建成功！')
                    else:
                        logger.info(f'[ {UPLOAD_REMOTE_PATH} ] 远程文件夹已存在')
                    continue
                except FileNotFoundError:
                    logger.error(
                        f"远程目标路径[ {UPLOAD_REMOTE_PATH} ]的父级文件夹不存在，请创建父级目录或重新确认目标路径是否有误")
                    break
            else:
                logger.warning(f"本地无文件, {UPLOAD_TIME_INTERVAL / 2}秒后再次扫描上传......")
            logger.info("===================================================================")
            time.sleep(UPLOAD_TIME_INTERVAL / 2)
        except Exception as e:
            logger.error(f"{repr(e)}")
            logger.info(f"将在5秒后重连服务器...")
            time.sleep(5)
            sftp_client.reconnect()


if __name__ == '__main__':
    # 创建日志目录
    create_log_folder()
    logging.config.dictConfig(LOGGING_CONFIG)  # logging config使能输出
    # 运行主程序
    main()
