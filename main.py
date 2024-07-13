import json
import os
import re
import gzip
import shutil
import time
import aiohttp
import asyncio
import requests
from tqdm import tqdm
import disk_sync
from loguru import logger

os_arch = "amd64"
# 配置logger，将日志信息存储到文件中
logger.add("log_file.log", rotation="500 MB", retention="10 days", compression="zip")

def init():
    current_path = os.getcwd()
    if not os.path.exists(f"{current_path}/cache"):
        os.mkdir(f"{current_path}/cache")
    if not os.path.exists(f"{current_path}/mirror"):
        os.mkdir(f"{current_path}/mirror")


def make_index():
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
        categories = ["main"]
        for categorie in categories:
            current_path = os.getcwd()
            logger.info(f"begin make {os_version_tag}_{categorie} all file list")
            index_dir = f"{current_path}/{os_version_tag}/{categorie}"
            if not os.path.exists(index_dir) or not os.path.isdir(index_dir):
                os.makedirs(index_dir)
            full_url = f"{os_url}/dists/{os_version_tag}/{categorie}/binary-{os_arch}/Packages.gz"
            full_path = f"{index_dir}/Packages.gz"
            download_packageinfo_file(full_url, full_path)
            extract_gz(full_path, f"{index_dir}/Packages")
            package_info = parse_package_info(file_name=f"{index_dir}/Packages", url=os_url)
            # j_package_info = json.dump(package_info)
            if os.path.exists(f"{current_path}/cache/{os_version_tag}_{categorie}.json"):
                os.remove(f"{current_path}/cache/{os_version_tag}_{categorie}.json")
            with open(f"{current_path}/cache/{os_version_tag}_{categorie}.json", 'w') as j_Package_info:
                json.dump(package_info, j_Package_info)


def download_packageinfo_file(url, local_filename):
    try:
        # 检查文件是否存在并删除
        if os.path.exists(local_filename):
            os.remove(local_filename)
            logger.info(f"Existing file '{local_filename}' removed.")

        # 发起网络请求并下载文件
        with requests.get(url, stream=True) as r:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # 确保请求成功
            total_size = int(response.headers.get('content-length', 0))
            with open(local_filename, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        bar.update(len(chunk))
        logger.debug(f"File '{local_filename}' downloaded successfully.")

    except requests.RequestException as e:
        logger.error(f"Error during requests to {url}: {e}")
    except IOError as e:
        logger.error(f"Error opening or writing to file '{local_filename}': {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


def extract_gz(file_path, output_path):
    try:
        # 检查源文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        # 解压文件
        with gzip.open(file_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        logger.info(f"File '{file_path}' has been extracted to '{output_path}'.")

    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
    except gzip.BadGzipFile as e:
        logger.error(f"Error with gzip file: {e}")
    except IOError as e:
        logger.error(f"IO error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


def parse_package_info(file_name, url):
    with open(file_name, 'r', encoding='utf-8') as FILE_NAME:
        info_str = FILE_NAME.read()
    # 以两个换行符分割包信息
    packages = info_str.strip().split("\n\n")
    package_dicts = []
    # 生成所有包的列表开始遍历
    for package in packages:
        # 初始化变量
        deb_package_name = None
        file_path = None
        single_package_download_url = None

        # 以行分割包信息 开始遍历单个包信息
        single_package_info_list = package.split("\n")

        for line in single_package_info_list:
            if 'Package:' in line:
                deb_package_name = line.split(':', 1)[1].strip()
            elif 'Filename:' in line:
                file_path = line.split(':', 1)[1].strip()
                single_package_download_url = f"{url}/{file_path}"

        # 确保在字典中只保存有用信息
        if deb_package_name is not None and file_path is not None:
            package_info = {"Name": deb_package_name, "Download_url": single_package_download_url}
            package_dicts.append(package_info)
            logger.info(package_info)
    return package_dicts


# gpt
# def parse_package_info(info_str):
#     # 以两个换行符分割包信息
#     packages = info_str.strip().split("\n\n")
#     package_dicts = []
#
#     for package in packages:
#         # 提取每个包的信息
#         fields = re.findall(r'^(\w[\w-]+):\s*(.*)$', package, re.MULTILINE)
#         package_dict = {}
#         for key, value in fields:
#             if key in package_dict:
#                 # 如果键已存在，追加值
#                 package_dict[key] += f", {value}"
#             else:
#                 package_dict[key] = value
#         package_dicts.append(package_dict)
#
#     return package_dicts
#
#
# def print_package_dicts(package_dicts):
#     for idx, package_dict in enumerate(package_dicts, start=1):
#         print(f"\nPackage {idx}:")
#         for key, value in package_dict.items():
#             print(f"{key}: {value}")


def get_download_url():
    current_path = os.getcwd()
    file_path = f"{current_path}/cache"
    try:
        # 获取目录下的所有文件
        items = os.listdir(file_path)

        # 过滤出文件
        files = [item for item in items if os.path.isfile(os.path.join(file_path, item))]

        for file in files:
            logger.info(f"begin download {file.split('.json')[0]} packages")
            all_packages_url_list = []
            with open(os.path.join(file_path, file), 'r') as File:
                # 读取文件内容并打印
                file_content = File.read()

                # 解析 JSON 数据
                try:
                    download_info_list = json.loads(file_content)
                    if isinstance(download_info_list, list):
                        for download_info in download_info_list:
                            if isinstance(download_info, dict):
                                package_download_url = download_info.get('Download_url')
                                logger.info(package_download_url)
                                all_packages_url_list.append(package_download_url)
                            else:
                                logger.error("Expected a dictionary but got:", type(download_info))
                    else:
                        logger.error("Expected a list but got:", type(download_info_list))
                except json.JSONDecodeError as json_error:
                    logger.error(f"JSON decode error: {json_error}")
            asyncio.run(download_files(all_packages_url_list))
    except Exception as e:
        logger.error(f"Error: {e}")


async def download_file(session, url, local_filename):
    if os.path.exists(local_filename):
        logger.warning(f"File already exists: {local_filename}, skipping download.")
        return
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            with open(local_filename, 'wb') as file:
                while True:
                    chunk = await response.content.read(8192)
                    if not chunk:
                        break
                    file.write(chunk)
        logger.info(f"Downloaded {local_filename} from {url}")
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")


async def download_files(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            package_full_name = url.split('/')[-1]
            package_download_path = url.replace('https://', '')
            package_download_path = package_download_path.replace(f"{package_full_name}", '')
            current_path = os.getcwd()
            package_download_path = f"{current_path}/mirror/{package_download_path}"
            if not os.path.exists(package_download_path):
                os.makedirs(package_download_path)
            # filename = os.path.join(package_download_path, os.path.basename(url))
            tasks.append(download_file(session, url, f"{package_download_path}/{package_full_name}"))
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    init()
    make_index()
    get_download_url()
    disk_sync.get_dists()
    disk_sync.get_others()