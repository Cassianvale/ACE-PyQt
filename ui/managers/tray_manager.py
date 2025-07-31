#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""系统托盘管理器"""

import os
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSlot
from utils import logger, send_notification


class TrayManager:
    """系统托盘管理器，负责托盘图标和菜单管理"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.config_manager = main_window.config_manager
        self.icon_path = main_window.icon_path
        self.app_name = main_window.app_name

        # 托盘相关属性
        self.tray_icon = None
        self.toggle_window_action = None
        self.notify_action = None
        self.startup_action = None

    def setup_tray(self):
        """设置系统托盘图标"""
        self.tray_icon = QSystemTrayIcon(self.main_window)
        if self.icon_path:
            self.tray_icon.setIcon(QIcon(self.icon_path))
        else:
            self.tray_icon.setIcon(QIcon())

        # 创建托盘菜单
        tray_menu = self._create_tray_menu()
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

        # 初始更新托盘菜单项文本
        self.update_tray_menu_text()

    def _create_tray_menu(self):
        """创建托盘菜单"""
        tray_menu = QMenu()

        # 显示/隐藏主窗口动作
        self.toggle_window_action = QAction("显示主窗口", self.main_window)
        self.toggle_window_action.triggered.connect(self.toggle_main_window)
        tray_menu.addAction(self.toggle_window_action)

        # 显示状态动作
        status_action = QAction("显示状态", self.main_window)
        status_action.triggered.connect(self.show_status)
        tray_menu.addAction(status_action)

        tray_menu.addSeparator()

        # 启用通知动作
        self.notify_action = QAction("启用通知", self.main_window)
        self.notify_action.setCheckable(True)
        self.notify_action.triggered.connect(self._on_toggle_notifications_from_tray)
        tray_menu.addAction(self.notify_action)

        # 开机自启动动作
        self.startup_action = QAction("开机自启动", self.main_window)
        self.startup_action.setCheckable(True)
        self.startup_action.triggered.connect(self._on_toggle_auto_start_from_tray)
        tray_menu.addAction(self.startup_action)

        tray_menu.addSeparator()

        # 主题切换子菜单
        theme_menu = self._create_theme_menu()
        tray_menu.addMenu(theme_menu)

        tray_menu.addSeparator()

        # 打开配置目录动作
        config_dir_action = QAction("打开配置目录", self.main_window)
        config_dir_action.triggered.connect(self._on_open_config_dir)
        tray_menu.addAction(config_dir_action)

        # 检查更新动作
        check_update_action = QAction("检查更新", self.main_window)
        check_update_action.triggered.connect(self._on_check_update)
        tray_menu.addAction(check_update_action)

        tray_menu.addSeparator()

        # 退出动作
        exit_action = QAction("退出", self.main_window)
        exit_action.triggered.connect(self._on_confirm_exit)
        tray_menu.addAction(exit_action)

        return tray_menu

    def _create_theme_menu(self):
        """创建主题切换子菜单"""
        theme_menu = QMenu("主题设置")

        # 浅色主题动作
        light_theme_action = QAction("浅色", self.main_window)
        light_theme_action.triggered.connect(lambda: self._on_switch_theme("light"))
        theme_menu.addAction(light_theme_action)

        # 深色主题动作
        dark_theme_action = QAction("深色", self.main_window)
        dark_theme_action.triggered.connect(lambda: self._on_switch_theme("dark"))
        theme_menu.addAction(dark_theme_action)

        return theme_menu

    def toggle_main_window(self):
        """切换主窗口的显示状态"""
        if self.main_window.isHidden() or self.main_window.is_custom_minimized:
            # 如果窗口隐藏或是自定义最小化状态，则显示窗口
            if self.main_window.is_custom_minimized:
                self.main_window.event_handler.restore_from_custom_minimize()
            else:
                self.main_window.showNormal()
                self.main_window.activateWindow()
            logger.debug("从托盘菜单显示主窗口")
        else:
            # 如果窗口已显示，则最小化到托盘
            if hasattr(self.main_window, "custom_titlebar") and self.main_window.custom_titlebar:
                self.main_window.custom_titlebar.minimize_to_tray()
                logger.debug("从托盘菜单隐藏主窗口到托盘")
            else:
                self.main_window.hide()
                logger.debug("从托盘菜单隐藏主窗口")

        self.update_tray_menu_text()

    def update_tray_menu_text(self):
        """更新托盘菜单项文本"""
        if self.toggle_window_action:
            if self.main_window.isHidden() or self.main_window.is_custom_minimized:
                self.toggle_window_action.setText("显示主窗口")
            else:
                self.toggle_window_action.setText("隐藏窗口到托盘")

    def show_status(self):
        """在托盘菜单显示状态通知"""
        status = self._get_status_info()
        send_notification(title=f"{self.app_name} 状态", message=status, icon_path=self.icon_path)

    def _get_status_info(self):
        """获取应用状态信息"""
        status_lines = []
        status_lines.append(f"🟢 {self.app_name} 正在运行")
        status_lines.append(f"📱 通知: {'已启用' if self.config_manager.show_notifications else '已禁用'}")
        status_lines.append(f"🚀 开机自启: {'已启用' if self.config_manager.auto_start else '已禁用'}")
        status_lines.append(f"🎨 主题: {'浅色模式' if self.config_manager.theme == 'light' else '深色模式'}")
        status_lines.append(f"🪟 关闭行为: {'最小化到托盘' if self.config_manager.close_to_tray else '直接退出'}")
        return "\n".join(status_lines)

    def tray_icon_activated(self, reason):
        """处理托盘图标激活事件(处理 C++ 枚举到 Python 的转换问题)"""
        try:
            # 优先使用 value 属性比较，这是最可靠的方法
            if hasattr(reason, "value"):
                if reason.value == QSystemTrayIcon.ActivationReason.DoubleClick.value:
                    self.toggle_main_window()
            else:
                # 备用方案：直接比较枚举
                if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
                    self.toggle_main_window()
        except Exception as e:
            logger.debug(f"托盘图标激活事件处理失败: {e}")

    def show_tray_message(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information, timeout=3000):
        """显示托盘通知消息"""
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, timeout)

    def hide_tray(self):
        """隐藏托盘图标"""
        if self.tray_icon:
            self.tray_icon.hide()

    # 事件回调方法 - 这些方法会调用主窗口的相应方法
    def _on_toggle_notifications_from_tray(self):
        """从托盘菜单切换通知开关的回调"""
        if hasattr(self.main_window, "settings_manager"):
            self.main_window.settings_manager.toggle_notifications_from_tray()

    def _on_toggle_auto_start_from_tray(self):
        """从托盘菜单切换自启动开关的回调"""
        if hasattr(self.main_window, "settings_manager"):
            self.main_window.settings_manager.toggle_auto_start_from_tray()

    def _on_switch_theme(self, theme):
        """切换主题的回调"""
        if hasattr(self.main_window, "theme_manager"):
            self.main_window.theme_manager.switch_theme(theme)

    def _on_open_config_dir(self):
        """打开配置目录的回调"""
        if hasattr(self.main_window, "event_handler"):
            self.main_window.event_handler.open_config_dir()

    def _on_check_update(self):
        """检查更新的回调"""
        if hasattr(self.main_window, "version_manager"):
            self.main_window.version_manager.check_update()

    def _on_confirm_exit(self):
        """确认退出的回调"""
        if hasattr(self.main_window, "event_handler"):
            self.main_window.event_handler.confirm_exit()
