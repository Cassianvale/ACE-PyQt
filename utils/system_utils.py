#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统工具函数模块
"""

import ctypes
import os
import sys
import subprocess
from .logger import logger
from config.app_config import APP_INFO


def run_as_admin():
    """
    判断是否以管理员权限运行，如果不是则尝试获取管理员权限
    
    Returns:
        bool: 是否以管理员权限运行
    """
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        return False
    return True


def check_single_instance(mutex_name=None):
    """
    检查程序是否已经在运行，确保只有一个实例
    
    Args:
        mutex_name (str, optional): 互斥体名称，如果不提供则使用默认名称
    
    Returns:
        bool: 如果是首次运行返回True，否则返回False
    """
    if mutex_name is None:
        app_name = APP_INFO["name"]
        mutex_name = f"Global\\{app_name}_MUTEX"
        
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    if ctypes.windll.kernel32.GetLastError() == 183:
        logger.warning("程序已经在运行中，无法启动多个实例！")
        
        # 显示提醒弹窗
        show_already_running_dialog(APP_INFO["name"])
        return False
    return True


def show_already_running_dialog(app_name=None):
    """
    显示程序已运行的提醒对话框
    
    Args:
        app_name (str): 应用名称
    """
    if app_name is None:
        app_name = APP_INFO["name"]
        
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
            0x00000040 | 0x00040000  # MB_ICONINFORMATION | MB_TOPMOST
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
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        # 直接运行的python脚本
        return os.path.abspath(sys.argv[0])


def check_auto_start(app_name=None):
    """
    检查是否设置了开机自启（使用任务计划程序）
    
    Args:
        app_name (str): 应用名称
    
    Returns:
        bool: 是否设置了开机自启
    """
    if app_name is None:
        app_name = APP_INFO["name"]
        
    try:
        # 清理任务名称，避免特殊字符
        task_name = f"{app_name}_AutoStart".replace(" ", "_")
        
        # 使用schtasks命令查询任务是否存在
        result = subprocess.run(
            ["schtasks", "/query", "/tn", task_name],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # 如果返回码为0，表示任务存在
        return result.returncode == 0
            
    except Exception as e:
        logger.error(f"检查开机自启状态失败: {str(e)}")
        return False


def enable_auto_start(app_name=None):
    """
    设置开机自启（使用任务计划程序，可跳过UAC以管理员权限运行）
    
    Args:
        app_name (str): 应用名称
        
    Returns:
        bool: 操作是否成功
    """
    if app_name is None:
        app_name = APP_INFO["name"]
        
    try:
        # 清理任务名称，避免特殊字符
        task_name = f"{app_name}_AutoStart".replace(" ", "_")
        
        # 获取当前程序路径
        program_path = get_program_path()
        
        # 构建任务运行命令（程序路径 + --minimized参数）
        task_command = f'"{program_path}" --minimized'
        
        # 使用schtasks命令创建任务
        # /create: 创建新任务
        # /tn: 任务名称
        # /tr: 要运行的程序
        # /sc onlogon: 登录时触发
        # /rl highest: 以最高权限运行（跳过UAC）
        # /f: 强制创建，覆盖现有任务
        result = subprocess.run([
            "schtasks", "/create",
            "/tn", task_name,
            "/tr", task_command,
            "/sc", "onlogon",
            "/rl", "highest",
            "/f"
        ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode == 0:
            logger.debug(f"已设置开机自启（任务计划程序），任务名称: {task_name}")
            logger.debug(f"任务将以管理员权限运行，跳过UAC提示")
            return True
        else:
            logger.error(f"设置开机自启失败，错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"设置开机自启失败: {str(e)}")
        return False


def disable_auto_start(app_name=None):
    """
    取消开机自启（删除任务计划程序中的任务）
    
    Args:
        app_name (str): 应用名称
        
    Returns:
        bool: 操作是否成功
    """
    if app_name is None:
        app_name = APP_INFO["name"]
        
    try:
        # 清理任务名称，避免特殊字符
        task_name = f"{app_name}_AutoStart".replace(" ", "_")
        
        # 使用schtasks命令删除任务
        # /delete: 删除任务
        # /tn: 任务名称
        # /f: 强制删除，不提示确认
        result = subprocess.run([
            "schtasks", "/delete",
            "/tn", task_name,
            "/f"
        ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode == 0:
            logger.debug(f"已取消开机自启，删除任务计划程序任务: {task_name}")
            return True
        else:
            # 如果任务不存在，返回码通常是1，这也算成功
            if "不存在" in result.stderr or "does not exist" in result.stderr.lower() or "找不到指定的文件" in result.stderr:
                logger.debug(f"任务计划程序任务不存在，无需删除: {task_name}")
                return True
            else:
                logger.error(f"取消开机自启失败，错误信息: {result.stderr}")
                return False
        
    except Exception as e:
        logger.error(f"取消开机自启失败: {str(e)}")
        return False


 