#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""版本检查UI管理器"""

import webbrowser
import os
from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import QSystemTrayIcon
from ui.styles import StyleHelper
from utils import logger, get_version_checker, create_update_message


class VersionManager:
    """版本检查UI管理器，负责版本检查相关的UI处理"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.config_manager = main_window.config_manager
        self.app_name = main_window.app_name
        self.github_releases_url = main_window.github_releases_url
        
        # 版本检查器
        self.version_checker = get_version_checker(self.config_manager)
        self.download_url = None
        
    def initialize_version_checker(self):
        """初始化版本检查器"""
        self.version_checker.check_finished.connect(self._on_version_check_finished)
        
    def check_update(self):
        """检查更新"""
        if not hasattr(self.main_window, 'check_update_btn'):
            return
            
        # 显示正在检查的消息
        self.main_window.check_update_btn.setText("检查中...")
        self.main_window.check_update_btn.setEnabled(False)
        
        # 异步检查更新
        self.version_checker.check_for_updates_async()
        
    def _on_version_check_finished(self, has_update, current_ver, latest_ver, update_info_str, error_msg):
        """版本检查完成的处理函数"""
        # 恢复按钮状态
        if hasattr(self.main_window, 'check_update_btn'):
            self.main_window.check_update_btn.setText("检查更新")
            self.main_window.check_update_btn.setEnabled(True)
            
        # 检测是否为静默模式
        silent_mode = error_msg == "silent_mode"
        
        # 保存下载URL
        self.download_url = None
        if has_update and update_info_str:
            try:
                import json
                update_info = json.loads(update_info_str)
                self.download_url = update_info.get("download_url")
                if not self.download_url:
                    self.download_url = update_info.get("url", self.github_releases_url)
            except:
                self.download_url = self.github_releases_url
                
        # 更新版本显示标签
        self._update_version_label(has_update, current_ver, latest_ver)
        
        # 如果是静默模式，只更新界面不显示弹窗
        if silent_mode:
            logger.debug(f"静默检查更新中，有更新: {has_update}")
            # 如果有更新，在托盘图标中显示简短提示
            if has_update and self.config_manager.show_notifications:
                if hasattr(self.main_window, 'tray_manager') and self.main_window.tray_manager.tray_icon:
                    self.main_window.tray_manager.show_tray_message(
                        self.app_name,
                        f"发现新版本 v{latest_ver} 可用",
                        QSystemTrayIcon.MessageIcon.Information,
                        3000
                    )
            return
            
        # 显示更新对话框
        self._show_update_dialog(has_update, current_ver, latest_ver, update_info_str, error_msg)
        
    def _update_version_label(self, has_update, current_ver, latest_ver):
        """更新版本显示标签"""
        if not hasattr(self.main_window, 'version_label'):
            return
            
        if has_update and latest_ver:
            # 添加HTML链接，设置为可点击状态
            self.main_window.version_label.setText(
                f"当前版本: v{current_ver} | 🆕 <b>最新版本: v{latest_ver} </b> <a href='#download' style='color: #28C940; font-weight: bold; font-size: 14px; text-decoration: none;'> 👉 前往下载</a>"
            )
            self.main_window.version_label.setOpenExternalLinks(False)
            self.main_window.version_label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
            # 连接到下载函数
            self.main_window.version_label.linkActivated.connect(self._open_download_page)
            StyleHelper.set_label_type(self.main_window.version_label, "warning")
        else:
            self.main_window.version_label.setText(f"当前版本: v{current_ver}")
            StyleHelper.set_label_type(self.main_window.version_label, "info")
            
    def _show_update_dialog(self, has_update, current_ver, latest_ver, update_info_str, error_msg):
        """显示更新对话框"""
        # 创建并显示消息
        result = create_update_message(
            has_update, current_ver, latest_ver, update_info_str, error_msg, self.github_releases_url
        )
        
        # 解包结果
        title, message, msg_type, extra_data = result
        
        if hasattr(self.main_window, 'dialog_manager'):
            if msg_type == "error":
                self.main_window.dialog_manager.show_update_error_dialog(title, message, extra_data)
            elif msg_type == "update":
                self.main_window.dialog_manager.show_update_available_dialog(title, message, extra_data)
            else:
                self.main_window.dialog_manager.show_info_dialog(title, message)
                
    def _open_download_url(self, download_url=None, is_direct_download=False):
        """
        打开下载链接或发布页面
        
        Args:
            download_url: 下载链接，如果为None则使用GitHub发布页面
            is_direct_download: 是否为直接下载链接
        """
        try:
            # 确定最终使用的下载URL
            final_url = download_url if download_url else self.github_releases_url
            
            # 如果是直接下载链接
            if is_direct_download:
                # 在Windows上使用默认浏览器下载
                if os.name == "nt":
                    os.startfile(final_url)
                else:
                    webbrowser.open(final_url)
                logger.debug(f"用户直接下载新版本: {final_url}")
            else:
                # 如果不是直接下载链接，打开网页
                webbrowser.open(final_url)
                logger.debug(f"用户访问下载页面: {final_url}")
                
            return True
        except Exception as e:
            logger.error(f"打开下载链接失败: {str(e)}")
            if hasattr(self.main_window, 'dialog_manager'):
                self.main_window.dialog_manager.show_warning_dialog("错误", f"打开下载链接失败: {str(e)}")
            return False
            
    def _open_download_page(self, link):
        """
        通过版本标签链接触发下载
        
        Args:
            link: 链接文本
        """
        if self.download_url:
            self._open_download_url(self.download_url, is_direct_download=True)
        else:
            self._open_download_url(self.github_releases_url, is_direct_download=False)