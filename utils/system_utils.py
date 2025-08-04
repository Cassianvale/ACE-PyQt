#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统工具函数模块

提供Windows系统相关的工具函数，包括管理员权限检查、单实例运行、开机自启等功能。
"""

import ctypes
import os
import sys
import winreg
from .logger import logger


def run_as_admin():
    """
    判断是否以管理员权限运行，如果不是则尝试获取管理员权限

    Returns:
        bool: 是否以管理员权限运行
    """
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return False
    return True


def check_single_instance(mutex_name):
    """
    检查程序是否已经在运行，确保只有一个实例

    Args:
        mutex_name (str): 互斥体名称，必须提供

    Returns:
        bool: 如果是首次运行返回True，否则返回False
    """
    if not mutex_name:
        raise ValueError("mutex_name 参数不能为空")

    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    if ctypes.windll.kernel32.GetLastError() == 183:
        logger.warning("程序已经在运行中，无法启动多个实例！")
        return False
    return True


def show_already_running_dialog(app_name):
    """
    显示程序已运行的提醒对话框

    Args:
        app_name (str): 应用名称，必须提供
    """
    if not app_name:
        raise ValueError("app_name 参数不能为空")

    try:
        # 使用Windows API显示消息框
        message = (
            f"{app_name} 已经在运行中！\n\n"
            "程序只允许运行一个实例。\n"
            f"请检查系统托盘是否有{app_name}图标。\n\n"
            "如果找不到运行中的程序，请尝试：\n"
            f"• 检查任务管理器中是否有{app_name}进程\n"
            "• 重启电脑后再次运行程序"
        )

        title = "程序已在运行中"

        # 使用Windows API显示消息框
        # MB_OK = 0x00000000, MB_ICONINFORMATION = 0x00000040, MB_TOPMOST = 0x00040000
        ctypes.windll.user32.MessageBoxW(
            0,  # 父窗口句柄
            message,  # 消息内容
            title,  # 标题
            0x00000040 | 0x00040000,  # MB_ICONINFORMATION | MB_TOPMOST
        )

        logger.debug("已显示程序重复运行提醒对话框")

    except Exception as e:
        logger.error(f"显示程序重复运行对话框失败: {str(e)}")
        # 如果显示对话框失败，至少在控制台输出信息
        print(f"{app_name} 已经在运行中，无法启动多个实例！")


def get_program_path():
    """
    获取程序完整路径

    Returns:
        str: 程序完整路径
    """
    if getattr(sys, "frozen", False):
        return sys.executable
    else:
        # 直接运行的python脚本
        return os.path.abspath(sys.argv[0])


def check_auto_start(app_name=None, program_path=None):
    """
    检查是否设置了开机自启（使用注册表）

    Args:
        app_name (str, optional): 应用名称，如果不提供则从配置中获取
        program_path (str, optional): 程序路径，用于验证注册表中的路径是否正确

    Returns:
        bool: 是否设置了开机自启
    """
    if app_name is None:
        try:
            from config.app_config import APP_INFO

            app_name = APP_INFO["name"]
        except ImportError:
            raise ValueError("app_name 参数不能为空，且无法从配置中获取")

    try:
        # 打开注册表键
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ
        ) as key:
            try:
                # 尝试读取应用的注册表项
                value, _ = winreg.QueryValueEx(key, app_name)

                # 如果提供了程序路径，验证注册表中的路径是否匹配
                if program_path:
                    # 规范化路径进行比较
                    current_path = os.path.normpath(program_path)
                    registry_path = value.strip('"').split()[0]  # 移除引号和参数
                    registry_path = os.path.normpath(registry_path)

                    if current_path.lower() == registry_path.lower():
                        logger.debug(f"开机自启已设置且路径正确: {app_name} -> {value}")
                        return True
                    else:
                        logger.warning(f"开机自启路径不匹配: 当前={current_path}, 注册表={registry_path}")
                        return False
                else:
                    # 如果没有提供路径，只检查是否存在
                    logger.debug(f"开机自启已设置: {app_name} -> {value}")
                    return True

            except FileNotFoundError:
                # 注册表项不存在
                logger.debug(f"开机自启未设置: {app_name}")
                return False

    except Exception as e:
        logger.error(f"检查开机自启状态失败: {str(e)}")
        return False


def enable_auto_start(app_name=None, program_path=None, startup_args=None):
    """
    设置开机自启（使用注册表）

    Args:
        app_name (str, optional): 应用名称，如果不提供则从配置中获取
        program_path (str, optional): 程序路径，如果不提供则使用当前程序路径
        startup_args (list, optional): 启动参数列表，如 ["--minimized"]

    Returns:
        bool: 操作是否成功
    """
    if app_name is None:
        try:
            from config.app_config import APP_INFO

            app_name = APP_INFO["name"]
        except ImportError:
            raise ValueError("app_name 参数不能为空，且无法从配置中获取")

    try:
        # 获取程序路径
        if program_path is None:
            program_path = get_program_path()

        # 构建启动命令
        if startup_args:
            command = f'"{program_path}" {" ".join(startup_args)}'
        else:
            # 默认添加 --minimized 参数，保持与原来任务计划程序实现的兼容性
            command = f'"{program_path}" --minimized'

        # 打开注册表键进行写入
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE
        ) as key:
            # 设置注册表值
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)

        logger.debug(f"已设置开机自启（注册表）: {app_name} -> {command}")
        return True

    except PermissionError:
        logger.error(f"设置开机自启失败: 权限不足，无法写入注册表")
        return False
    except Exception as e:
        logger.error(f"设置开机自启失败: {str(e)}")
        return False


def disable_auto_start(app_name=None):
    """
    取消开机自启（删除注册表中的项）

    Args:
        app_name (str, optional): 应用名称，如果不提供则从配置中获取

    Returns:
        bool: 操作是否成功
    """
    if app_name is None:
        try:
            from config.app_config import APP_INFO

            app_name = APP_INFO["name"]
        except ImportError:
            raise ValueError("app_name 参数不能为空，且无法从配置中获取")

    try:
        # 打开注册表键进行删除
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE
        ) as key:
            try:
                # 删除注册表项
                winreg.DeleteValue(key, app_name)
                logger.debug(f"已取消开机自启: {app_name}")
                return True
            except FileNotFoundError:
                return True

    except PermissionError:
        logger.error(f"取消开机自启失败: 权限不足，无法修改注册表")
        return False
    except Exception as e:
        logger.error(f"取消开机自启失败: {str(e)}")
        return False
