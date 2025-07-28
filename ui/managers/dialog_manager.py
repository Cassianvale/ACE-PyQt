#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""对话框管理器"""

import webbrowser
from PyQt6.QtWidgets import QMessageBox
from utils import logger


class DialogManager:
    """对话框管理器，负责各种对话框的创建和处理"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.config_manager = main_window.config_manager
        self.app_name = main_window.app_name
        self.app_author = main_window.app_author
        self.app_description = main_window.app_description
        self.github_repo = main_window.github_repo

    def show_about_dialog(self):
        """显示关于对话框"""
        # 创建自定义消息框，添加访问官网的选项
        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle("关于")
        msg_box.setText(
            f"{self.app_name}\n\n"
            f"作者: {self.app_author}\n\n"
            f"描述: {self.app_description}\n\n"
            "💡 如果这个工具对您有帮助，欢迎访问GitHub项目页面：\n"
            "   • 点击⭐Star支持项目发展\n"
            "   • 提交Issues反馈问题和建议\n"
            "   • 分享给更多需要的朋友\n\n"
            "您的支持是项目持续改进的动力！\n\n"
            "是否访问项目官网？"
        )
        msg_box.setIcon(QMessageBox.Icon.NoIcon)

        # 添加自定义按钮
        visit_btn = msg_box.addButton("⭐ 访问GitHub主页", QMessageBox.ButtonRole.ActionRole)
        close_btn = msg_box.addButton("❌ 关闭", QMessageBox.ButtonRole.RejectRole)

        # 设置默认按钮
        msg_box.setDefaultButton(visit_btn)

        # 执行对话框并处理结果
        msg_box.exec()
        clicked_button = msg_box.clickedButton()

        # 如果点击了访问官网按钮
        if clicked_button == visit_btn:
            github_url = f"https://github.com/{self.github_repo}"
            webbrowser.open(github_url)
            logger.debug("用户通过关于对话框访问了项目官网")

    def show_update_error_dialog(self, title, message, extra_data):
        """显示更新错误对话框"""
        msg_box = QMessageBox(self.main_window)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        # 添加自定义按钮
        get_version_btn = msg_box.addButton("🌐 前往下载页面", QMessageBox.ButtonRole.YesRole)
        cancel_btn = msg_box.addButton("❌ 关闭", QMessageBox.ButtonRole.NoRole)
        msg_box.setDefaultButton(cancel_btn)

        msg_box.exec()
        if msg_box.clickedButton() == get_version_btn:
            github_url = extra_data.get("github_url", self.main_window.github_releases_url)
            webbrowser.open(github_url)

    def show_update_available_dialog(self, title, message, extra_data):
        """显示有更新可用对话框"""
        msg_box = QMessageBox(self.main_window)
        msg_box.setIcon(QMessageBox.Icon.NoIcon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        # 根据是否为直接下载调整按钮配置
        is_direct_download = extra_data.get("is_direct_download", False)
        if is_direct_download:
            direct_btn = msg_box.addButton("🌐 下载更新", QMessageBox.ButtonRole.AcceptRole)
            cancel_btn = msg_box.addButton("❌ 关闭", QMessageBox.ButtonRole.RejectRole)
            msg_box.setDefaultButton(direct_btn)
        else:
            # 没有直接下载链接时，只提供页面跳转
            download_btn = msg_box.addButton("🌐 前往下载页面", QMessageBox.ButtonRole.AcceptRole)
            cancel_btn = msg_box.addButton("❌ 关闭", QMessageBox.ButtonRole.RejectRole)
            msg_box.setDefaultButton(download_btn)

        msg_box.exec()
        clicked_button = msg_box.clickedButton()

        # 处理下载按钮点击
        download_url = extra_data.get("download_url")
        is_direct_download = extra_data.get("is_direct_download", False)
        should_download = False

        if is_direct_download:
            # 有直接下载链接的情况
            if clicked_button == direct_btn:
                should_download = True
        else:
            # 没有直接下载链接的情况
            if clicked_button == download_btn:
                should_download = True

        # 执行下载
        if should_download and hasattr(self.main_window, "version_manager"):
            self.main_window.version_manager._open_download_url(download_url, is_direct_download)

    def show_info_dialog(self, title, message):
        """显示信息对话框"""
        QMessageBox.information(self.main_window, title, message)

    def show_warning_dialog(self, title, message):
        """显示警告对话框"""
        QMessageBox.warning(self.main_window, title, message)

    def show_error_dialog(self, title, message):
        """显示错误对话框"""
        QMessageBox.critical(self.main_window, title, message)

    def show_question_dialog(self, title, message):
        """显示询问对话框"""
        return QMessageBox.question(self.main_window, title, message)
