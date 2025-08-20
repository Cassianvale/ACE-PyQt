#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主程序入口
"""

import os
import sys
import queue
import argparse

from config import ConfigManager, APP_INFO, DEFAULT_CONFIG, SYSTEM_CONFIG
from utils import (
    run_as_admin,
    check_single_instance,
    logger,
    setup_logger,
    find_icon_path,
    send_notification,
    create_notification_thread,
    check_for_update,
)


def main(custom_app_info=None, custom_default_config=None, custom_system_config=None):
    """
    主程序入口函数

    Args:
        custom_app_info (dict, optional): 自定义应用信息，用于覆盖默认值
        custom_default_config (dict, optional): 自定义默认配置，用于覆盖默认值
        custom_system_config (dict, optional): 自定义系统配置，用于覆盖默认值
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="ACE-PyQt 应用程序")
    parser.add_argument("--minimized", action="store_true", help="以最小化模式启动")
    parser.add_argument("--gui", choices=["old", "new"], default="new", help="选择GUI模式")
    args = parser.parse_args()
    
    start_minimized = args.minimized

    # 合并应用信息
    final_app_info = APP_INFO.copy()
    if custom_app_info:
        final_app_info.update(custom_app_info)

    # 合并系统配置
    final_system_config = SYSTEM_CONFIG.copy()
    if custom_system_config:
        final_system_config.update(custom_system_config)

    # 检查管理员权限
    if final_system_config.get("require_admin_privileges", True):
        if not run_as_admin():
            return

    # 检查单实例运行
    mutex_name = f"Global\\{final_app_info['name'].replace(' ', '_')}_MUTEX"
    if not check_single_instance(mutex_name):
        return

    # 创建配置管理器
    config_manager = ConfigManager(
        custom_app_info=final_app_info,
        custom_default_config=custom_default_config,
        custom_system_config=final_system_config,
    )

    # 初始化日志系统
    setup_logger(
        log_dir=config_manager.log_dir,
        log_retention_days=config_manager.log_retention_days,
        log_rotation=config_manager.log_rotation,
        debug_mode=config_manager.debug_mode,
    )

    logger.debug("🟩 程序已启动！")

    icon_path = find_icon_path()

    # 通知线程
    notification_thread_obj, stop_event = create_notification_thread(queue.Queue(), icon_path)

    # 根据参数选择GUI模式
    if args.gui == "new":
        # 使用新的PyQt-Fluent-Widgets界面
        from app.main_window import MainWindow
        from contextlib import redirect_stdout
        
        with redirect_stdout(None):
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import Qt
        
        # 启用高DPI支持
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        app = QApplication(sys.argv)
        window = MainWindow()
        
        if not start_minimized:
            window.show()
    else:
        # 使用原有的UI界面（向后兼容）
        try:
            from ui import create_gui
            app, window = create_gui(config_manager, icon_path, start_minimized)
        except ImportError:
            logger.error("旧版UI模块无法导入，请使用 --gui new 参数")
            return

    app_name = config_manager.get_app_name()
    app_author = config_manager.get_app_author()
    github_repo = config_manager.get_github_repo()
    github_releases = config_manager.get_github_releases_url()

    if config_manager.check_update_on_start:
        logger.debug("启动时检查更新已开启，执行静默检查更新...")
        check_for_update(config_manager, silent_mode=True)

    buttons = [
        {"text": "访问项目官网", "action": "open_url", "launch": f"https://github.com/{github_repo}"},
        {"text": "下载最新版本", "action": "open_url", "launch": github_releases},
    ]

    # 不受Windows通知选项限制，每次开启都显示通知
    send_notification(
        title=app_name,
        message=f"🚀 欢迎使用 {app_name} ！\n🐶 作者: {app_author}",
        icon_path=icon_path,
        buttons=buttons,
        silent=True,  # 通知是否静音
    )

    try:
        # 运行应用（这会阻塞主线程直到应用程序退出）
        sys.exit(app.exec())
    except KeyboardInterrupt:
        # 处理键盘中断
        pass
    finally:
        # 停止通知线程
        if stop_event:
            stop_event.set()

        logger.debug("🔴 程序已终止！")


if __name__ == "__main__":
    main()
