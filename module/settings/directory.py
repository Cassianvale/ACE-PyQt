#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置目录操作业务逻辑
"""

import os
import subprocess
import platform
from pathlib import Path
from utils.logger import logger
from module.config import cfg


class DirectoryManager:
    """配置目录管理业务逻辑"""
    
    @staticmethod
    def open_config_directory() -> bool:
        """
        打开配置文件目录
        
        Returns:
            bool: 操作是否成功
        """
        try:
            config_dir = Path(cfg.config_dir)
            
            # 确保目录存在
            if not config_dir.exists():
                config_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建配置目录: {config_dir}")
            
            # 根据操作系统打开目录
            if platform.system() == "Windows":
                os.startfile(str(config_dir))
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(config_dir)])
            else:  # Linux and other Unix-like systems
                subprocess.run(["xdg-open", str(config_dir)])
            
            logger.info(f"已打开配置目录: {config_dir}")
            return True
            
        except Exception as e:
            logger.error(f"打开配置目录失败: {str(e)}")
            return False
    
    @staticmethod
    def open_log_directory() -> bool:
        """
        打开日志文件目录
        
        Returns:
            bool: 操作是否成功
        """
        try:
            log_dir = Path(cfg.log_dir)
            
            # 确保目录存在
            if not log_dir.exists():
                log_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建日志目录: {log_dir}")
            
            # 根据操作系统打开目录
            if platform.system() == "Windows":
                os.startfile(str(log_dir))
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(log_dir)])
            else:  # Linux and other Unix-like systems
                subprocess.run(["xdg-open", str(log_dir)])
            
            logger.info(f"已打开日志目录: {log_dir}")
            return True
            
        except Exception as e:
            logger.error(f"打开日志目录失败: {str(e)}")
            return False
    
    @staticmethod
    def get_config_directory() -> str:
        """
        获取配置文件目录路径
        
        Returns:
            str: 配置文件目录路径
        """
        return str(cfg.config_dir)
    
    @staticmethod
    def get_log_directory() -> str:
        """
        获取日志文件目录路径
        
        Returns:
            str: 日志文件目录路径
        """
        return str(cfg.log_dir)
    
    @staticmethod
    def get_config_file_path() -> str:
        """
        获取配置文件完整路径
        
        Returns:
            str: 配置文件完整路径
        """
        return str(cfg.config_file)
    
    @staticmethod
    def ensure_directories() -> bool:
        """
        确保所有必要的目录存在
        
        Returns:
            bool: 操作是否成功
        """
        try:
            # 确保配置目录存在
            config_dir = Path(cfg.config_dir)
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # 确保日志目录存在
            log_dir = Path(cfg.log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            logger.debug("所有必要目录已确保存在")
            return True
            
        except Exception as e:
            logger.error(f"创建必要目录失败: {str(e)}")
            return False