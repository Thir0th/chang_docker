#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Docker镜像源自动更新脚本
功能：从指定来源爬取最新镜像源，更新系统daemon.json配置并重启Docker服务
"""

import os
import sys
import json
import logging
import subprocess
import requests
from datetime import datetime
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/var/log/docker_mirror_updater.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("docker_mirror_updater")

# 配置文件路径
DAEMON_JSON_PATH = "/etc/docker/daemon.json"
# 镜像源获取地址（可根据需要添加或修改）
MIRROR_SOURCES = [
    "https://cloud.tencent.com/developer/article/2485043",
    "https://blog.csdn.net/c12312303/article/details/146428465"
]
# 备用镜像源（当爬取失败时使用）
FALLBACK_MIRRORS = [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
]
# 脚本执行日志路径
LOG_PATH = "/var/log/docker_mirror_updater.log"

def get_mirrors_from_url(url):
    """从URL获取镜像源列表"""
    try:
        logger.info(f"正在从 {url} 爬取镜像源列表")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 检查请求是否成功
        
        # 根据不同网站结构提取镜像源（这里需要根据实际网页结构调整）
        content = response.text
        
        # 示例：从CSDN文章中提取镜像源（实际需要根据网页结构调整正则表达式）
        if "csdn" in urlparse(url).netloc:
            # 简单示例，实际应根据网页结构编写更精确的正则表达式
            mirrors = set()
            # 这里应添加从CSDN文章中提取镜像源的逻辑
            return list(mirrors)
        
        # 示例：从腾讯云文章中提取镜像源
        elif "cloud.tencent" in urlparse(url).netloc:
            mirrors = set()
            # 这里应添加从腾讯云文章中提取镜像源的逻辑
            return list(mirrors)
        
        logger.warning(f"不支持的URL格式: {url}")
        return []
        
    except requests.exceptions.RequestException as e:
        logger.error(f"从 {url} 获取镜像源失败: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"处理 {url} 时发生异常: {str(e)}")
        return []

def get_available_mirrors():
    """获取所有可用的镜像源"""
    all_mirrors = set()
    
    # 从所有来源获取镜像源
    for source in MIRROR_SOURCES:
        mirrors = get_mirrors_from_url(source)
        all_mirrors.update(mirrors)
    
    # 如果没有获取到镜像源，使用备用镜像源
    if not all_mirrors:
        logger.warning("未从网络获取到镜像源，使用备用镜像源")
        all_mirrors.update(FALLBACK_MIRRORS)
    
    # 去重并转换为列表
    return list(all_mirrors)

def update_daemon_json(mirrors):
    """更新daemon.json配置文件"""
    try:
        # 读取当前配置
        current_config = {}
        if os.path.exists(DAEMON_JSON_PATH):
            try:
                with open(DAEMON_JSON_PATH, 'r') as f:
                    current_config = json.load(f)
                logger.info("已读取当前daemon.json配置")
            except json.JSONDecodeError:
                logger.warning("当前daemon.json格式错误，将创建新配置")
        
        # 更新镜像源
        current_config["registry-mirrors"] = mirrors
        
        # 写入新配置
        with open(DAEMON_JSON_PATH, 'w') as f:
            json.dump(current_config, f, indent=4)
        
        logger.info(f"已更新daemon.json，镜像源数量: {len(mirrors)}")
        return True
    
    except Exception as e:
        logger.error(f"更新daemon.json失败: {str(e)}")
        return False

def restart_docker_service():
    """重启Docker服务"""
    try:
        logger.info("正在重启Docker服务")
        # 使用subprocess执行系统命令
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "restart", "docker"], check=True)
        logger.info("Docker服务重启成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"重启Docker服务失败，错误码: {e.returncode}")
        return False
    except Exception as e:
        logger.error(f"重启Docker服务时发生异常: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("=== Docker镜像源自动更新脚本启动 ===")
    
    # 获取可用镜像源
    mirrors = get_available_mirrors()
    if not mirrors:
        logger.error("无法获取任何可用镜像源，脚本退出")
        return 1
    
    logger.info(f"获取到 {len(mirrors)} 个可用镜像源: {', '.join(mirrors[:3])}...")
    
    # 更新配置文件
    if update_daemon_json(mirrors):
        # 重启Docker服务
        restart_docker_service()
    
    logger.info("=== Docker镜像源更新完成 ===")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.critical(f"脚本执行过程中发生严重错误: {str(e)}")
        sys.exit(1)
