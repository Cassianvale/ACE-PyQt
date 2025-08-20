#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""窗口主题管理器 - UI层主题同步，业务逻辑已迁移到module层"""

from PyQt5.QtCore import pyqtSlot
from ui.styles import StyleHelper, theme_manager
from app.tools import logger
from module.theme.theme_manager import ThemeManager
from module.config import cfg


class WindowThemeManager:
    """窗口主题管理器 - 仅负责UI层主题同步，业务逻辑已分离"""

    def __init__(self, main_window):
        self.main_window = main_window
        # 保持向后兼容
        self.config_manager = getattr(main_window, 'config_manager', cfg)
        self.current_theme = getattr(main_window, 'current_theme', ThemeManager.get_current_theme())

    def initialize_theme(self):
        """初始化主题系统"""
        # 连接主题切换信号
        theme_manager.theme_changed.connect(self.apply_component_properties)

        # 应用初始主题
        theme_manager.set_theme(self.current_theme)

    @pyqtSlot(str)
    def switch_theme(self, theme):
        """
        切换应用程序主题 - 使用业务逻辑层

        Args:
            theme: 主题类型，可以是 "light", "dark" 或 "auto"
        """
        if theme != self.current_theme:
            # 使用业务逻辑层切换主题
            success = ThemeManager.switch_theme(theme)
            if success:
                self.current_theme = theme
                if hasattr(self.main_window, 'current_theme'):
                    self.main_window.current_theme = theme

                # 使用UI层主题管理器
                theme_manager.set_theme(theme)
                logger.debug(f"主题已设置为: {theme}")

                # 应用组件属性
                self.apply_component_properties()
            else:
                logger.error(f"主题切换失败: {theme}")

    def apply_component_properties(self):
        """应用组件属性"""
        try:
            # 设置无边框窗口透明背景属性
            StyleHelper.set_frameless_window_properties(self.main_window)

            # 设置按钮类型属性
            self.setup_button_properties()

            # 设置标签类型属性
            self.setup_label_properties()

            # 重新绘制窗口以应用新主题
            self.main_window.update()

        except Exception as e:
            logger.error(f"应用组件属性失败: {str(e)}")

    def setup_button_properties(self):
        """设置按钮属性"""
        if hasattr(self.main_window, "ui_manager"):
            self.main_window.ui_manager.setup_button_properties(self.current_theme)

    def setup_label_properties(self):
        """设置标签属性"""
        try:
            # 重新应用主题状态标签的样式
            if hasattr(self.main_window, "current_theme_label"):
                theme_name = "浅色" if self.current_theme == "light" else "深色"
                icon = "☀️" if self.current_theme == "light" else "🌙"
                status_text = f"{icon} 当前状态：{theme_name}主题"
                label_type = "success" if self.current_theme == "light" else "info"

                self.main_window.current_theme_label.setText(status_text)
                StyleHelper.set_label_type(self.main_window.current_theme_label, label_type)

        except Exception as e:
            logger.error(f"设置标签属性失败: {str(e)}")

    def get_theme_display_name(self):
        """获取主题的显示名称 - 使用业务逻辑层"""
        return ThemeManager.get_theme_display_name(self.current_theme)
