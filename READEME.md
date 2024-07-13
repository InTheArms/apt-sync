# 工具介绍

该工具用于同步指定版本的 Ubuntu 镜像资源。

## 同步前准备

### 1. 准备 `sources.list` 文件

请创建一个名为 `sources.list` 的文件，内容如下所示：

```plaintext
deb http://config1.cloud.qianxin-inc.cn:8389/ubuntu jammy main restricted universe multiverse
deb http://config1.cloud.qianxin-inc.cn:8389/ubuntu jammy-updates main restricted universe multiverse
deb http://config1.cloud.qianxin-inc.cn:8389/ubuntu jammy-backports main restricted universe multiverse
deb http://config1.cloud.qianxin-inc.cn:8389/ubuntu jammy-security main restricted universe multiverse
deb http://config1.cloud.qianxin-inc.cn:8389/ubuntu jammy-proposed main restricted universe multiverse
```
注意：请不要添加 deb-src 行，解析文件会出问题。

### 2. 安装依赖并运行脚本
在运行 main.py 之前，请确保安装必要的 Python 包。建议使用 Python 3.9 以上的版本。

使用以下命令安装依赖包：
```shell
pip install loguru tqdm aiohttp requests
```
然后运行脚本：
```shell
python main.py
```

### 3.其他问题
同步时间取决于您的网速、服务器性能等其他因素。同步完成后，会在 main.py 同级目录下生成以下目录：
```plaintext
    cache：缓存文件目录。
    jammy：下载的包链接目录（根据 sources.list 文件中的版本命名）。
    mirror：镜像源同步后的目录。
```


您可以直接映射 mirror 目录到 nginx。