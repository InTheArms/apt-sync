import os
import subprocess
from loguru import logger

# 配置logger，将日志信息存储到文件中
logger.add("log_file.log", rotation="500 MB", retention="10 days", compression="zip")

def get_dists():
    with open('sources.list', 'r') as FILE:
        apt_list = FILE.readlines()
    for mirror in apt_list:
        mirror = mirror.strip()
        if not mirror:  # 如果是空行，跳过
            continue
        parts = mirror.split()
        if len(parts) < 3:
            continue  # 跳过格式不正确的行
        os_version_tag = mirror.strip().split(' ')[2]
        os_url = mirror.strip().split(' ')[1]
        if os_url.endswith('/'):
            os_url = os_url[:-1]
        logger.debug(os_url)
        # 设置要下载的种类
        categories = ["main", "multiverse", "restricted", "universe"]
        # categories = ["main"]
        for categorie in categories:
            current_path = os.getcwd()
            logger.info(f"begin make {os_version_tag}_{categorie} all file list")
            rsync_url = f"rsync://{os_url.replace('https://', '')}/dists/{os_version_tag}-{categorie}"
            rsync_path = f"{current_path}/mirror/{os_url.replace('https://', '').split('/')[0]}/ubuntu/dists/"
            command = f"rsync -av {rsync_url} {rsync_path}"
            logger.info(rsync_path)
            logger.info(command)
            logger.info(rsync_url)
            try:
                result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
                if result.stdout:
                    logger.info(result.stdout)
                if result.stderr:
                    logger.error(result.stderr)
                logger.info(f"Sync completed successfully from {rsync_url} to {rsync_path}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Rsync command failed with error: {e}")
                if e.stdout:
                    logger.error(e.stdout)
                if e.stderr:
                    logger.error(e.stderr)


def get_others():
    current_path = os.getcwd()
    with open('sources.list', 'r') as FILE:
        apt_list = FILE.readlines()
    for mirror in apt_list:
        mirror = mirror.strip()
        if not mirror:  # 如果是空行，跳过
            continue
        parts = mirror.split()
        if len(parts) < 3:
            continue  # 跳过格式不正确的行
        os_version_tag = mirror.strip().split(' ')[2]
        os_url = mirror.strip().split(' ')[1]
        if os_url.endswith('/'):
            os_url = os_url[:-1]
        logger.debug(os_url)
        others_list = ["indices", "ls-lR.gz", "project"]
        for other in others_list:
            rsync_url = f"rsync://{os_url.replace('https://', '')}/{other}"
            rsync_path = f"{current_path}/mirror/ubuntu"
            command = f"rsync -av {rsync_url}  {rsync_path}"
            logger.info(rsync_path)
            logger.info(command)
            logger.info(rsync_url)
            try:
                result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
                if result.stdout:
                    logger.info(result.stdout)
                if result.stderr:
                    logger.error(result.stderr)
                logger.info(f"Sync completed successfully from {rsync_url} to {rsync_path}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Rsync command failed with error: {e}")
                if e.stdout:
                    logger.error(e.stdout)
                if e.stderr:
                    logger.error(e.stderr)


if __name__ == '__main__':
    get_dists()
    get_others()
