#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
重构后的PyQt6 GUI界面模块
"""

import os
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# 使用包导入
from utils import logger
from ui.styles import StyleApplier

# 导入管理器和处理器
from ui.managers import (
    UIManager,
    WindowThemeManager,
    TrayManager,
    SettingsManager,
    VersionManager,
    DialogManager,
)
from ui.handlers import EventHandler


class MainWindow(QWidget):
    """重构后的主窗口 - 作为各个管理器的协调者"""

    def __init__(self, config_manager, icon_path=None, start_minimized=False):
        super().__init__()

        # 基础属性
        self.config_manager = config_manager
        self.icon_path = icon_path
        self.current_theme = config_manager.theme
        self.start_minimized = start_minimized

        # 获取应用信息
        self.app_name = config_manager.get_app_name()
        self.app_author = config_manager.get_app_author()
        self.app_description = config_manager.get_app_description()
        self.github_repo = config_manager.get_github_repo()
        self.github_releases_url = config_manager.get_github_releases_url()

        # 自定义标题栏最小化相关
        self.is_custom_minimized = False

        # 定时器
        self.update_timer = None

        # 初始化管理器
        self._initialize_managers()

        # 设置UI
        self._setup_ui()

        # 设置托盘
        self._setup_tray()

        # 初始化主题系统
        self._initialize_theme()

        # 加载设置
        self._load_settings()

        # 连接信号
        self._connect_signals()

        # 设置定时器
        self._setup_timer()

        # 初始应用组件属性
        self.theme_manager.apply_component_properties()

    def _initialize_managers(self):
        """初始化所有管理器"""
        self.ui_manager = UIManager(self)
        self.theme_manager = WindowThemeManager(self)
        self.tray_manager = TrayManager(self)
        self.settings_manager = SettingsManager(self)
        self.version_manager = VersionManager(self)
        self.dialog_manager = DialogManager(self)
        self.event_handler = EventHandler(self)

    def _setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle(self.app_name)
        self.setMinimumSize(700, 800)

        # 设置无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowSystemMenuHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

        if self.icon_path and os.path.exists(self.icon_path):
            self.setWindowIcon(QIcon(self.icon_path))

        # 使用UI管理器设置布局
        self.ui_manager.setup_main_layout()

        # 创建所有选项卡
        self.ui_manager.create_all_tabs()

    def _setup_tray(self):
        """设置系统托盘"""
        self.tray_manager.setup_tray()

    def _initialize_theme(self):
        """初始化主题系统"""
        self.theme_manager.initialize_theme()

    def _load_settings(self):
        """加载设置"""
        self.settings_manager.load_settings()

    def _connect_signals(self):
        """连接信号"""
        # 连接设置相关信号
        self.settings_manager.connect_signals()

        # 连接事件处理器信号
        self.event_handler.setup_signals()

        # 初始化版本检查器
        self.version_manager.initialize_version_checker()

    def _setup_timer(self):
        """设置定时器"""
        self.event_handler.setup_timer()

    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        self.event_handler.handle_show_event(event)

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.event_handler.handle_close_event(event)


def create_gui(config_manager, icon_path=None, start_minimized=False):
    """
    创建图形用户界面

    Args:
        config_manager: 配置管理器对象
        icon_path: 图标路径
        start_minimized: 是否以最小化模式启动

    Returns:
        (QApplication, MainWindow): 应用程序对象和主窗口对象
    """

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # 应用Ant Design全局主题样式
    StyleApplier.apply_ant_design_theme(app)

    window = MainWindow(config_manager, icon_path, start_minimized)

    # 如果设置了最小化启动，则不显示主窗口
    if not start_minimized:
        window.show()
    else:
        logger.debug("程序以最小化模式启动，隐藏主窗口")

    return app, window
