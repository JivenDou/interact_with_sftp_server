# SFTP服务器交互程序

## 目录结构：

```
├─core（核心程序文件）
│  ├─Enum.py（枚举类 和 通用常量 定义）
│  └─sftp_client.py（连接以SFTP协议搭建的SFTP服务器客户端类）
├─config.ini（项目信息配置文件）
├─local_upload_to_sftp.py（上传文件脚本）
├─logging_config.py（日志信息配置脚本）
├─main_sftp.py（主进程入口）
├─sftp_download_to_local.py（下载文件脚本）
```

## 运行：

运行主程序：

```shell
python main_sftp.py
```
