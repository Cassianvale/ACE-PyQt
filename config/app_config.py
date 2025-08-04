#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模块
"""

# 应用程序基本信息
APP_INFO = {
    "name": "ACE-PyQt",  # 应用名称
    "author": "CassianVale",  # 作者
    "version": "1.0.0",  # 版本号（会被GitHub Actions构建时替换）
    "description": "PyQt6桌面应用程序框架",  # 应用描述
    "github_repo": "Cassianvale/ACE-PyQt",  # GitHub仓库
    "github_api_url": "https://api.github.com/repos/Cassianvale/ACE-PyQt/releases/latest",  # GitHub API URL
    "github_releases_url": "https://github.com/Cassianvale/ACE-PyQt/releases",  # GitHub发布页面URL
}

# 用户默认配置
DEFAULT_CONFIG = {
    "notifications": {"enabled": True},  # 通知默认开启
    "logging": {
        "retention_days": 7,  # 日志保留天数
        "rotation": "1 day",  # 日志轮转周期
        "debug_mode": False,  # 调试模式默认关闭
    },
    "application": {
        "auto_start": False,  # 开机自启动默认关闭
        "close_to_tray": True,  # 关闭窗口时默认最小化到托盘
        "theme": "light",  # 默认浅色主题
        "check_update_on_start": True,  # 启动时检查更新默认开启
    },
    "window": {"width": 700, "height": 800},  # 默认窗口尺寸
}

# 系统配置
SYSTEM_CONFIG = {
    "config_dir_name": ".ace-pyqt",  # 配置目录名称
    "log_dir_name": "logs",  # 日志目录名称
    "config_file_name": "config.yaml",  # 配置文件名称
    "network_timeout": 10,  # 网络请求超时时间（秒）
    "require_admin_privileges": False,  # 是否要求管理员权限启动应用程序
}
