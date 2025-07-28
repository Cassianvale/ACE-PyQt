#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""事件处理器"""

import os
import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtCore import QTimer
from utils import logger


class EventHandler:
    """事件处理器，负责各种用户交互和系统事件的处理"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.config_manager = main_window.config_manager
        self.app_name = main_window.app_name

    def setup_signals(self):
        """设置信号连接"""
        # 主题切换按钮信号
        if hasattr(self.main_window, "light_theme_btn"):
            self.main_window.light_theme_btn.clicked.connect(lambda: self._on_switch_theme("light"))
        if hasattr(self.main_window, "dark_theme_btn"):
            self.main_window.dark_theme_btn.clicked.connect(lambda: self._on_switch_theme("dark"))

        # 操作按钮信号
        if hasattr(self.main_window, "config_dir_btn"):
            self.main_window.config_dir_btn.clicked.connect(self.open_config_dir)
        if hasattr(self.main_window, "check_update_btn"):
            self.main_window.check_update_btn.clicked.connect(self._on_check_update)
        if hasattr(self.main_window, "about_btn"):
            self.main_window.about_btn.clicked.connect(self._on_show_about)

    def setup_timer(self):
        """设置定时器"""
        self.main_window.update_timer = QTimer(self.main_window)
        self.main_window.update_timer.start(1000)

    def open_config_dir(self):
        """打开配置目录"""
        try:
            if os.path.exists(self.config_manager.config_dir):
                if sys.platform == "win32":
                    os.startfile(self.config_manager.config_dir)
                else:
                    subprocess.Popen(["xdg-open", self.config_manager.config_dir])
                logger.debug(f"已打开配置目录: {self.config_manager.config_dir}")
            else:
                os.makedirs(self.config_manager.config_dir, exist_ok=True)
                if sys.platform == "win32":
                    os.startfile(self.config_manager.config_dir)
                else:
                    subprocess.Popen(["xdg-open", self.config_manager.config_dir])
                logger.debug(f"已创建并打开配置目录: {self.config_manager.config_dir}")
        except Exception as e:
            logger.error(f"打开配置目录失败: {str(e)}")
            if hasattr(self.main_window, "dialog_manager"):
                self.main_window.dialog_manager.show_warning_dialog("错误", f"打开配置目录失败: {str(e)}")

    def restore_from_custom_minimize(self):
        """从自定义标题栏最小化状态恢复窗口"""
        if hasattr(self.main_window, "custom_titlebar") and self.main_window.custom_titlebar:
            self.main_window.custom_titlebar.safe_restore_window()
            logger.debug("使用safe_restore_window()方法恢复窗口")
        else:
            # 否则使用简单恢复
            self.main_window.setWindowOpacity(1.0)
            self.main_window.show()
            self.main_window.showNormal()
            self.main_window.activateWindow()
            self.main_window.is_custom_minimized = False
            logger.debug("主窗口已恢复")

    def confirm_exit(self):
        """确认退出程序"""
        self.exit_app()

    def exit_app(self):
        """退出应用程序"""
        # 停止定时器（在主线程中处理）
        if hasattr(self.main_window, "update_timer") and self.main_window.update_timer:
            self.main_window.update_timer.stop()

        # 隐藏托盘图标（在主线程中处理）
        if hasattr(self.main_window, "tray_manager") and self.main_window.tray_manager.tray_icon:
            self.main_window.tray_manager.hide_tray()

        # 退出应用
        QApplication.quit()

    def handle_close_event(self, event):
        """处理窗口关闭事件"""
        # 根据配置设置执行相应操作
        if self.config_manager.close_to_tray:
            # 最小化到后台
            event.ignore()
            self.main_window.hide()
            if hasattr(self.main_window, "tray_manager"):
                self.main_window.tray_manager.update_tray_menu_text()
            # 如果托盘图标可见且通知开启，显示最小化提示
            if (
                hasattr(self.main_window, "tray_manager")
                and self.main_window.tray_manager.tray_icon
                and self.main_window.tray_manager.tray_icon.isVisible()
                and self.config_manager.show_notifications
            ):
                self.main_window.tray_manager.show_tray_message(
                    self.app_name,
                    "程序已最小化到系统托盘，继续在后台运行",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000,
                )
        else:
            # 直接退出程序
            event.accept()
            self.exit_app()

    def handle_show_event(self, event):
        """处理窗口显示事件"""
        # 重置自定义最小化标志
        self.main_window.is_custom_minimized = False
        if hasattr(self.main_window, "tray_manager"):
            self.main_window.tray_manager.update_tray_menu_text()

    # 内部回调方法
    def _on_switch_theme(self, theme):
        """切换主题的回调"""
        if hasattr(self.main_window, "theme_manager"):
            self.main_window.theme_manager.switch_theme(theme)

    def _on_check_update(self):
        """检查更新的回调"""
        if hasattr(self.main_window, "version_manager"):
            self.main_window.version_manager.check_update()

    def _on_show_about(self):
        """显示关于对话框的回调"""
        if hasattr(self.main_window, "dialog_manager"):
            self.main_window.dialog_manager.show_about_dialog()
