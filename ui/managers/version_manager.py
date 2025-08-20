#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""版本检查UI管理器 - UI层版本显示，业务逻辑已迁移到module层"""

import webbrowser
import os
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QSystemTrayIcon
from ui.styles import StyleHelper
from utils.logger import logger
from module.update.update_manager import UpdateManager
from module.config import cfg


class VersionManager:
    """版本检查UI管理器 - 仅负责UI层版本显示，业务逻辑已分离"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        # 保持向后兼容
        self.config_manager = getattr(main_window, 'config_manager', cfg)
        self.app_name = getattr(main_window, 'app_name', cfg.get_app_name())
        self.github_releases_url = getattr(main_window, 'github_releases_url', cfg.get_github_releases_url())
        
        # 使用业务逻辑层的更新管理器
        self.update_manager = UpdateManager()
        self.update_manager.initialize()
        
    def initialize_version_checker(self):
        """初始化版本检查器"""
        if hasattr(self.update_manager.version_checker, 'check_finished'):
            self.update_manager.version_checker.check_finished.connect(self._on_version_check_finished)
        
    def check_update(self):
        """检查更新 - 使用业务逻辑层"""
        if not hasattr(self.main_window, 'check_update_btn'):
            return
            
        # 显示正在检查的消息
        self.main_window.check_update_btn.setText("检查中...")
        self.main_window.check_update_btn.setEnabled(False)
        
        # 使用业务逻辑层检查更新
        self.update_manager.check_for_updates(silent_mode=False)
        
    def _on_version_check_finished(self, has_update, current_ver, latest_ver, update_info_str, error_msg):
        """版本检查完成的处理函数 - 使用业务逻辑层处理结果"""
        # 恢复按钮状态
        if hasattr(self.main_window, 'check_update_btn'):
            self.main_window.check_update_btn.setText("检查更新")
            self.main_window.check_update_btn.setEnabled(True)
            
        # 使用业务逻辑层处理更新结果
        result = self.update_manager.process_update_result(
            has_update, current_ver, latest_ver, update_info_str, error_msg
        )
        
        # 更新版本显示标签
        if hasattr(self.main_window, 'version_label'):
            self.main_window.version_label.setText(result['version_info'])
            if result['has_update']:
                self.main_window.version_label.setOpenExternalLinks(False)
                self.main_window.version_label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
                # 连接到下载函数
                self.main_window.version_label.linkActivated.connect(self._open_download_page)
                StyleHelper.set_label_type(self.main_window.version_label, "warning")
            else:
                StyleHelper.set_label_type(self.main_window.version_label, "info")
        
        # 如果是静默模式，只更新界面不显示弹窗
        if result.get('silent_mode'):
            logger.debug(f"静默检查更新中，有更新: {has_update}")
            # 如果有更新，在托盘图标中显示简短提示
            if has_update and cfg.show_notifications:
                if hasattr(self.main_window, 'tray_manager') and self.main_window.tray_manager.tray_icon:
                    self.main_window.tray_manager.show_tray_message(
                        self.app_name,
                        f"发现新版本 v{latest_ver} 可用",
                        QSystemTrayIcon.MessageIcon.Information,
                        3000
                    )
            return
            
        # 显示更新对话框
        if 'dialog' in result:
            self._show_update_dialog_from_result(result['dialog'])
        
    def _show_update_dialog_from_result(self, dialog_data):
        """根据业务逻辑层的结果显示更新对话框"""
        if hasattr(self.main_window, 'dialog_manager'):
            if dialog_data['type'] == "error":
                self.main_window.dialog_manager.show_update_error_dialog(
                    dialog_data['title'], dialog_data['message'], dialog_data['extra_data']
                )
            elif dialog_data['type'] == "update":
                self.main_window.dialog_manager.show_update_available_dialog(
                    dialog_data['title'], dialog_data['message'], dialog_data['extra_data']
                )
            else:
                self.main_window.dialog_manager.show_info_dialog(
                    dialog_data['title'], dialog_data['message']
                )
            
                
    def _open_download_url(self, download_url=None, is_direct_download=False):
        """
        打开下载链接或发布页面 - 使用业务逻辑层
        
        Args:
            download_url: 下载链接，如果为None则使用GitHub发布页面
            is_direct_download: 是否为直接下载链接
        """
        success = self.update_manager.open_download_url(download_url, is_direct_download)
        if not success and hasattr(self.main_window, 'dialog_manager'):
            self.main_window.dialog_manager.show_warning_dialog("错误", "打开下载链接失败")
        return success
            
    def _open_download_page(self, link):
        """
        通过版本标签链接触发下载
        
        Args:
            link: 链接文本
        """
        download_url = getattr(self.update_manager, 'download_url', None)
        if download_url:
            self._open_download_url(download_url, is_direct_download=True)
        else:
            self._open_download_url(self.github_releases_url, is_direct_download=False)