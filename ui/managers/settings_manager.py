#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""设置管理器"""

from PyQt6.QtWidgets import QMessageBox
from utils import logger, enable_auto_start, disable_auto_start


class SettingsManager:
    """设置管理器，负责配置同步和UI更新"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.config_manager = main_window.config_manager

    def load_settings(self):
        """加载设置到界面"""
        try:
            # 设置通知选项
            if hasattr(self.main_window, "notify_checkbox"):
                self.main_window.notify_checkbox.setChecked(self.config_manager.show_notifications)
            if hasattr(self.main_window, "tray_manager") and self.main_window.tray_manager.notify_action:
                self.main_window.tray_manager.notify_action.setChecked(self.config_manager.show_notifications)

            # 设置开机自启动选项
            if hasattr(self.main_window, "startup_checkbox"):
                self.main_window.startup_checkbox.setChecked(self.config_manager.auto_start)
            if hasattr(self.main_window, "tray_manager") and self.main_window.tray_manager.startup_action:
                self.main_window.tray_manager.startup_action.setChecked(self.config_manager.auto_start)

            # 设置检查更新选项
            if hasattr(self.main_window, "check_update_on_start_checkbox"):
                self.main_window.check_update_on_start_checkbox.setChecked(self.config_manager.check_update_on_start)

            # 设置调试模式选项
            if hasattr(self.main_window, "debug_checkbox"):
                self.main_window.debug_checkbox.setChecked(self.config_manager.debug_mode)

            # 设置关闭行为选项
            if hasattr(self.main_window, "close_behavior_combo"):
                close_to_tray = self.config_manager.close_to_tray
                for i in range(self.main_window.close_behavior_combo.count()):
                    if self.main_window.close_behavior_combo.itemData(i) == close_to_tray:
                        self.main_window.close_behavior_combo.setCurrentIndex(i)
                        break

            logger.debug("界面设置加载完成")

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
        """通用通知切换方法"""
        if from_tray:
            if hasattr(self.main_window, "tray_manager") and self.main_window.tray_manager.notify_action:
                self.config_manager.show_notifications = self.main_window.tray_manager.notify_action.isChecked()
                # 同步更新主窗口选项
                if hasattr(self.main_window, "notify_checkbox"):
                    self.main_window.notify_checkbox.blockSignals(True)
                    self.main_window.notify_checkbox.setChecked(self.config_manager.show_notifications)
                    self.main_window.notify_checkbox.blockSignals(False)
        else:
            if hasattr(self.main_window, "notify_checkbox"):
                self.config_manager.show_notifications = self.main_window.notify_checkbox.isChecked()
                # 同步更新托盘菜单选项
                if hasattr(self.main_window, "tray_manager") and self.main_window.tray_manager.notify_action:
                    self.main_window.tray_manager.notify_action.blockSignals(True)
                    self.main_window.tray_manager.notify_action.setChecked(self.config_manager.show_notifications)
                    self.main_window.tray_manager.notify_action.blockSignals(False)

        # 保存配置
        if self.config_manager.save_config():
            logger.debug(f"通知状态已更改并保存: {'开启' if self.config_manager.show_notifications else '关闭'}")
        else:
            logger.warning(f"通知状态已更改但保存失败: {'开启' if self.config_manager.show_notifications else '关闭'}")

    def toggle_auto_start(self):
        """切换开机自启动开关"""
        self._toggle_auto_start(from_tray=False)

    def toggle_auto_start_from_tray(self):
        """从托盘菜单切换开机自启动开关"""
        self._toggle_auto_start(from_tray=True)

    def _toggle_auto_start(self, from_tray=False):
        """通用自启动切换方法"""
        if from_tray:
            if hasattr(self.main_window, "tray_manager") and self.main_window.tray_manager.startup_action:
                self.config_manager.auto_start = self.main_window.tray_manager.startup_action.isChecked()
                # 同步更新主窗口选项
                if hasattr(self.main_window, "startup_checkbox"):
                    self.main_window.startup_checkbox.blockSignals(True)
                    self.main_window.startup_checkbox.setChecked(self.config_manager.auto_start)
                    self.main_window.startup_checkbox.blockSignals(False)
        else:
            if hasattr(self.main_window, "startup_checkbox"):
                self.config_manager.auto_start = self.main_window.startup_checkbox.isChecked()
                # 同步更新托盘菜单选项
                if hasattr(self.main_window, "tray_manager") and self.main_window.tray_manager.startup_action:
                    self.main_window.tray_manager.startup_action.blockSignals(True)
                    self.main_window.tray_manager.startup_action.setChecked(self.config_manager.auto_start)
                    self.main_window.tray_manager.startup_action.blockSignals(False)

        # 修改注册表
        if self.config_manager.auto_start:
            enable_auto_start(self.main_window.app_name)
        else:
            disable_auto_start(self.main_window.app_name)

        # 保存配置
        if self.config_manager.save_config():
            logger.debug(f"开机自启状态已更改并保存: {'开启' if self.config_manager.auto_start else '关闭'}")
        else:
            logger.warning(f"开机自启状态已更改但保存失败: {'开启' if self.config_manager.auto_start else '关闭'}")

    def toggle_debug_mode(self):
        """切换调试模式"""
        if not hasattr(self.main_window, "debug_checkbox"):
            return

        # 获取新的调试模式状态
        new_debug_mode = self.main_window.debug_checkbox.isChecked()
        self.config_manager.debug_mode = new_debug_mode

        # 保存配置
        if self.config_manager.save_config():
            logger.debug(f"调试模式已更改并保存: {'开启' if new_debug_mode else '关闭'}")
        else:
            logger.warning(f"调试模式已更改但保存失败: {'开启' if new_debug_mode else '关闭'}")

        # 重新初始化日志系统
        from utils.logger import setup_logger

        setup_logger(
            log_dir=self.config_manager.log_dir,
            log_retention_days=self.config_manager.log_retention_days,
            log_rotation=self.config_manager.log_rotation,
            debug_mode=new_debug_mode,
        )

    def on_close_behavior_changed(self):
        """关闭行为选项变化时的处理"""
        if not hasattr(self.main_window, "close_behavior_combo"):
            return

        close_to_tray = self.main_window.close_behavior_combo.currentData()
        if close_to_tray is not None:
            self.config_manager.close_to_tray = close_to_tray

            # 保存配置
            if self.config_manager.save_config():
                logger.debug(f"关闭行为设置已更改并保存: {'最小化到后台' if close_to_tray else '直接退出'}")
            else:
                logger.warning(f"关闭行为设置已更改但保存失败: {'最小化到后台' if close_to_tray else '直接退出'}")

    def toggle_check_update_on_start(self):
        """切换启动时检查更新设置"""
        try:
            if not hasattr(self.main_window, "check_update_on_start_checkbox"):
                return

            # 获取当前复选框状态
            check_update_on_start = self.main_window.check_update_on_start_checkbox.isChecked()

            # 更新配置
            self.config_manager.check_update_on_start = check_update_on_start

            # 保存配置
            if self.config_manager.save_config():
                logger.debug(f"启动时检查更新设置已保存: {check_update_on_start}")
            else:
                logger.warning("启动时检查更新设置保存失败")

        except Exception as e:
            logger.error(f"切换启动时检查更新设置失败: {str(e)}")
            QMessageBox.warning(self.main_window, "错误", f"切换启动时检查更新设置失败: {str(e)}")

            # 恢复界面状态
            if hasattr(self.main_window, "check_update_on_start_checkbox"):
                self.main_window.check_update_on_start_checkbox.setChecked(self.config_manager.check_update_on_start)
