#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""设置管理器 - UI层设置同步，业务逻辑已迁移到module层"""

from PyQt5.QtWidgets import QMessageBox
from utils.logger import logger

# 业务逻辑模块
from module.settings.startup import StartupSettings
from module.settings.notifications import NotificationSettings
from module.settings.window import WindowSettings
from module.settings.logging import LoggingSettings
from module.config import cfg


class SettingsManager:
    """设置管理器 - 仅负责UI层设置同步，业务逻辑已分离"""

    def __init__(self, main_window):
        self.main_window = main_window
        # 保持向后兼容
        self.config_manager = main_window.config_manager if hasattr(main_window, 'config_manager') else cfg

    def load_settings(self):
        """加载设置到界面 - 使用业务逻辑层"""
        try:
            # 设置通知选项
            notification_status = NotificationSettings.get_notification_status()
            if hasattr(self.main_window, "notify_checkbox"):
                self.main_window.notify_checkbox.setChecked(notification_status)
            if hasattr(self.main_window, "tray_manager") and self.main_window.tray_manager.notify_action:
                self.main_window.tray_manager.notify_action.setChecked(notification_status)

            # 设置开机自启动选项
            auto_start_status = StartupSettings.get_auto_start_status()
            if hasattr(self.main_window, "startup_checkbox"):
                self.main_window.startup_checkbox.setChecked(auto_start_status)
            if hasattr(self.main_window, "tray_manager") and self.main_window.tray_manager.startup_action:
                self.main_window.tray_manager.startup_action.setChecked(auto_start_status)

            # 设置检查更新选项
            check_update_status = StartupSettings.get_check_update_on_start_status()
            if hasattr(self.main_window, "check_update_on_start_checkbox"):
                self.main_window.check_update_on_start_checkbox.setChecked(check_update_status)

            # 设置调试模式选项
            debug_status = LoggingSettings.get_debug_mode_status()
            if hasattr(self.main_window, "debug_checkbox"):
                self.main_window.debug_checkbox.setChecked(debug_status)

            # 设置关闭行为选项
            if hasattr(self.main_window, "close_behavior_combo"):
                close_to_tray = WindowSettings.get_close_behavior()
                for i in range(self.main_window.close_behavior_combo.count()):
                    if self.main_window.close_behavior_combo.itemData(i) == close_to_tray:
                        self.main_window.close_behavior_combo.setCurrentIndex(i)
                        break

        except Exception as e:
            logger.error(f"加载界面设置失败: {str(e)}")

    def connect_signals(self):
        """连接设置相关信号"""
        if hasattr(self.main_window, "notify_checkbox"):
            self.main_window.notify_checkbox.stateChanged.connect(self.toggle_notifications)
        if hasattr(self.main_window, "startup_checkbox"):
            self.main_window.startup_checkbox.stateChanged.connect(self.toggle_auto_start)
        if hasattr(self.main_window, "check_update_on_start_checkbox"):
            self.main_window.check_update_on_start_checkbox.stateChanged.connect(self.toggle_check_update_on_start)
        if hasattr(self.main_window, "debug_checkbox"):
            self.main_window.debug_checkbox.stateChanged.connect(self.toggle_debug_mode)
        if hasattr(self.main_window, "close_behavior_combo"):
            self.main_window.close_behavior_combo.currentIndexChanged.connect(self.on_close_behavior_changed)

    def toggle_notifications(self):
        """切换通知开关"""
        self._toggle_notifications(from_tray=False)

    def toggle_notifications_from_tray(self):
        """从托盘菜单切换通知开关"""
        self._toggle_notifications(from_tray=True)

    def _toggle_notifications(self, from_tray=False):
        """通用通知切换方法 - 使用业务逻辑层"""
        if from_tray:
            if hasattr(self.main_window, "tray_manager") and self.main_window.tray_manager.notify_action:
                enabled = self.main_window.tray_manager.notify_action.isChecked()
                success = NotificationSettings.toggle_notifications(enabled)
                if success:
                    # 同步更新主窗口选项
                    if hasattr(self.main_window, "notify_checkbox"):
                        self.main_window.notify_checkbox.blockSignals(True)
                        self.main_window.notify_checkbox.setChecked(enabled)
                        self.main_window.notify_checkbox.blockSignals(False)
        else:
            if hasattr(self.main_window, "notify_checkbox"):
                enabled = self.main_window.notify_checkbox.isChecked()
                success = NotificationSettings.toggle_notifications(enabled)
                if success:
                    # 同步更新托盘菜单选项
                    if hasattr(self.main_window, "tray_manager") and self.main_window.tray_manager.notify_action:
                        self.main_window.tray_manager.notify_action.blockSignals(True)
                        self.main_window.tray_manager.notify_action.setChecked(enabled)
                        self.main_window.tray_manager.notify_action.blockSignals(False)

    def toggle_auto_start(self):
        """切换开机自启动开关"""
        self._toggle_auto_start(from_tray=False)

    def toggle_auto_start_from_tray(self):
        """从托盘菜单切换开机自启动开关"""
        self._toggle_auto_start(from_tray=True)

    def _toggle_auto_start(self, from_tray=False):
        """通用自启动切换方法 - 使用业务逻辑层"""
        if from_tray:
            if hasattr(self.main_window, "tray_manager") and self.main_window.tray_manager.startup_action:
                enabled = self.main_window.tray_manager.startup_action.isChecked()
                app_name = getattr(self.main_window, 'app_name', cfg.get_app_name())
                success = StartupSettings.toggle_auto_start(enabled, app_name)
                if success:
                    # 同步更新主窗口选项
                    if hasattr(self.main_window, "startup_checkbox"):
                        self.main_window.startup_checkbox.blockSignals(True)
                        self.main_window.startup_checkbox.setChecked(enabled)
                        self.main_window.startup_checkbox.blockSignals(False)
        else:
            if hasattr(self.main_window, "startup_checkbox"):
                enabled = self.main_window.startup_checkbox.isChecked()
                app_name = getattr(self.main_window, 'app_name', cfg.get_app_name())
                success = StartupSettings.toggle_auto_start(enabled, app_name)
                if success:
                    # 同步更新托盘菜单选项
                    if hasattr(self.main_window, "tray_manager") and self.main_window.tray_manager.startup_action:
                        self.main_window.tray_manager.startup_action.blockSignals(True)
                        self.main_window.tray_manager.startup_action.setChecked(enabled)
                        self.main_window.tray_manager.startup_action.blockSignals(False)

    def toggle_debug_mode(self):
        """切换调试模式 - 使用业务逻辑层"""
        if not hasattr(self.main_window, "debug_checkbox"):
            return

        # 获取新的调试模式状态
        new_debug_mode = self.main_window.debug_checkbox.isChecked()
        success = LoggingSettings.toggle_debug_mode(new_debug_mode)
        
        if not success:
            # 恢复界面状态
            self.main_window.debug_checkbox.setChecked(LoggingSettings.get_debug_mode_status())

    def on_close_behavior_changed(self):
        """关闭行为选项变化时的处理 - 使用业务逻辑层"""
        if not hasattr(self.main_window, "close_behavior_combo"):
            return

        close_to_tray = self.main_window.close_behavior_combo.currentData()
        if close_to_tray is not None:
            WindowSettings.set_close_behavior(close_to_tray)

    def toggle_check_update_on_start(self):
        """切换启动时检查更新设置 - 使用业务逻辑层"""
        try:
            if not hasattr(self.main_window, "check_update_on_start_checkbox"):
                return

            # 获取当前复选框状态
            check_update_on_start = self.main_window.check_update_on_start_checkbox.isChecked()
            success = StartupSettings.toggle_check_update_on_start(check_update_on_start)
            
            if not success:
                # 恢复界面状态
                self.main_window.check_update_on_start_checkbox.setChecked(
                    StartupSettings.get_check_update_on_start_status()
                )

        except Exception as e:
            logger.error(f"切换启动时检查更新设置失败: {str(e)}")
            QMessageBox.warning(self.main_window, "错误", f"切换启动时检查更新设置失败: {str(e)}")

            # 恢复界面状态
            if hasattr(self.main_window, "check_update_on_start_checkbox"):
                self.main_window.check_update_on_start_checkbox.setChecked(
                    StartupSettings.get_check_update_on_start_status()
                )
