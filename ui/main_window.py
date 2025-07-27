#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyQt6 GUI界面模块
"""

import os
import sys
import threading
import subprocess
import time
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QCheckBox,
    QSystemTrayIcon,
    QMenu,
    QGroupBox,
    QTabWidget,
    QFrame,
    QMessageBox,
    QScrollArea,
    QGridLayout,
    QProgressDialog,
    QProgressBar,
    QComboBox,
    QSpinBox,
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer, QRectF
from PyQt6.QtGui import QIcon, QAction, QPainterPath, QRegion, QPainter, QBrush, QPen, QColor

# 使用包导入
from utils import (
    logger,
    get_version_checker,
    get_app_version,
    create_update_message,
    send_notification,
    enable_auto_start,
    disable_auto_start,
)
from ui.components.custom_titlebar import CustomTitleBar
from ui.styles import (
    ColorScheme,
    StyleHelper,
    theme_manager,
    StatusHTMLGenerator,
    StyleApplier,
    AntColors,
    AntColorsDark,
)


class MainWindow(QWidget):
    """主窗口"""

    def __init__(self, config_manager, icon_path=None, start_minimized=False):
        super().__init__()

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
        self.original_geometry = None

        # 初始化版本检查器
        self.version_checker = get_version_checker(config_manager)
        self.version_checker.check_finished.connect(self._on_version_check_finished)

        self.setup_ui()
        self.setup_tray()

        # 连接主题切换信号 - 当主题改变时自动应用组件属性
        theme_manager.theme_changed.connect(self.apply_component_properties)

        # 初始化定时器和设置
        self.update_timer = QTimer(self)
        self.update_timer.start(1000)

        # 应用初始主题
        theme_manager.set_theme(self.current_theme)

        # 初始加载设置
        self.load_settings()

        # 初始应用组件属性
        self.apply_component_properties()

    def load_settings(self):
        """加载设置到界面"""
        try:
            # 设置通知选项
            self.notify_checkbox.setChecked(self.config_manager.show_notifications)
            self.notify_action.setChecked(self.config_manager.show_notifications)

            # 设置开机自启动选项
            self.startup_checkbox.setChecked(self.config_manager.auto_start)
            self.startup_action.setChecked(self.config_manager.auto_start)

            # 设置检查更新选项
            self.check_update_on_start_checkbox.setChecked(self.config_manager.check_update_on_start)

            # 设置调试模式选项
            self.debug_checkbox.setChecked(self.config_manager.debug_mode)

            # 设置关闭行为选项
            close_to_tray = self.config_manager.close_to_tray
            for i in range(self.close_behavior_combo.count()):
                if self.close_behavior_combo.itemData(i) == close_to_tray:
                    self.close_behavior_combo.setCurrentIndex(i)
                    break

            logger.debug("界面设置加载完成")

        except Exception as e:
            logger.error(f"加载界面设置失败: {str(e)}")

    def showEvent(self, event):
        """窗口显示时应用圆角遮罩"""
        super().showEvent(event)
        # 重置自定义最小化标志
        self.is_custom_minimized = False
        self.update_tray_menu_text()

    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle(self.app_name)
        self.setMinimumSize(600, 800)

        # 设置无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowSystemMenuHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

        if self.icon_path and os.path.exists(self.icon_path):
            self.setWindowIcon(QIcon(self.icon_path))

        # 创建主布局 - 直接在QWidget上
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 添加自定义标题栏
        self.custom_titlebar = CustomTitleBar(self)
        main_layout.addWidget(self.custom_titlebar)

        # 创建内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(8, 0, 8, 8)
        main_layout.addWidget(content_widget)

        # 创建选项卡
        self.tabs = QTabWidget()
        content_layout.addWidget(self.tabs)

        # 设置选项卡
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)

        # 通知设置
        notify_group = QGroupBox("通知设置")
        notify_layout = QVBoxLayout()
        self.notify_checkbox = QCheckBox("启用Windows通知")
        self.notify_checkbox.stateChanged.connect(self.toggle_notifications)
        notify_layout.addWidget(self.notify_checkbox)
        notify_group.setLayout(notify_layout)
        settings_layout.addWidget(notify_group)

        # 启动设置
        startup_group = QGroupBox("启动设置")
        startup_layout = QVBoxLayout()
        self.startup_checkbox = QCheckBox("开机自启动")
        self.startup_checkbox.stateChanged.connect(self.toggle_auto_start)
        startup_layout.addWidget(self.startup_checkbox)

        # 添加启动时检查更新选项
        self.check_update_on_start_checkbox = QCheckBox("启动时检查更新")
        self.check_update_on_start_checkbox.stateChanged.connect(self.toggle_check_update_on_start)
        startup_layout.addWidget(self.check_update_on_start_checkbox)

        startup_group.setLayout(startup_layout)
        settings_layout.addWidget(startup_group)

        # 窗口行为设置
        window_group = QGroupBox("窗口行为设置")
        window_layout = QVBoxLayout()

        # 关闭行为选择
        close_behavior_layout = QHBoxLayout()
        close_behavior_label = QLabel("关闭窗口时:")
        close_behavior_layout.addWidget(close_behavior_label)

        self.close_behavior_combo = QComboBox()
        self.close_behavior_combo.addItem("最小化到系统托盘", True)
        self.close_behavior_combo.addItem("直接退出程序", False)
        self.close_behavior_combo.currentIndexChanged.connect(self.on_close_behavior_changed)
        close_behavior_layout.addWidget(self.close_behavior_combo)

        close_behavior_layout.addStretch()
        window_layout.addLayout(close_behavior_layout)

        # 添加说明文本
        close_behavior_info = QLabel("💡 最小化到系统托盘：程序将继续在后台运行\n💡 直接退出程序：完全关闭程序进程")
        close_behavior_info.setWordWrap(True)
        StyleHelper.set_label_type(close_behavior_info, "info")
        window_layout.addWidget(close_behavior_info)

        window_group.setLayout(window_layout)
        settings_layout.addWidget(window_group)

        # 日志设置
        log_group = QGroupBox("日志设置")
        log_layout = QVBoxLayout()
        self.debug_checkbox = QCheckBox("启用调试模式")
        self.debug_checkbox.stateChanged.connect(self.toggle_debug_mode)
        log_layout.addWidget(self.debug_checkbox)
        log_group.setLayout(log_layout)
        settings_layout.addWidget(log_group)

        # 主题设置
        theme_group = QGroupBox("主题设置")
        theme_layout = QVBoxLayout()

        # 主题选择水平布局
        theme_buttons_layout = QHBoxLayout()
        theme_buttons_layout.setSpacing(8)  # 增加按钮间距

        # 浅色主题按钮
        self.light_theme_btn = QPushButton("☀️ 浅色模式")
        self.light_theme_btn.clicked.connect(lambda: self.switch_theme("light"))
        self.light_theme_btn.setToolTip("切换到浅色主题模式")
        self.light_theme_btn.setMinimumHeight(32)  # 增加按钮高度
        theme_buttons_layout.addWidget(self.light_theme_btn)

        # 深色主题按钮
        self.dark_theme_btn = QPushButton("🌙 深色模式")
        self.dark_theme_btn.clicked.connect(lambda: self.switch_theme("dark"))
        self.dark_theme_btn.setToolTip("切换到深色主题模式")
        self.dark_theme_btn.setMinimumHeight(32)
        theme_buttons_layout.addWidget(self.dark_theme_btn)

        theme_layout.addLayout(theme_buttons_layout)
        theme_group.setLayout(theme_layout)
        settings_layout.addWidget(theme_group)

        # 添加操作按钮
        actions_group = QGroupBox("操作")
        actions_layout = QHBoxLayout()

        # 打开配置目录按钮
        self.config_dir_btn = QPushButton("打开配置目录")
        self.config_dir_btn.clicked.connect(self.open_config_dir)
        actions_layout.addWidget(self.config_dir_btn)

        # 检查更新按钮
        self.check_update_btn = QPushButton("检查更新")
        self.check_update_btn.clicked.connect(self.check_update)
        actions_layout.addWidget(self.check_update_btn)

        # 关于按钮
        self.about_btn = QPushButton("关于")
        self.about_btn.clicked.connect(self.show_about)
        actions_layout.addWidget(self.about_btn)

        actions_group.setLayout(actions_layout)
        settings_layout.addWidget(actions_group)

        # 版本信息显示
        version_group = QGroupBox("版本信息")
        version_layout = QVBoxLayout()

        # 获取当前版本号
        current_version = get_app_version(self.config_manager)
        self.version_label = QLabel(f"当前版本: v{current_version}")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        StyleHelper.set_label_type(self.version_label, "info")
        version_layout.addWidget(self.version_label)

        version_group.setLayout(version_layout)
        settings_layout.addWidget(version_group)

        # 添加空白占位
        settings_layout.addStretch()

        # 添加选项卡
        self.tabs.addTab(settings_tab, "  设置  ")

    def setup_tray(self):
        """设置系统托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)
        if self.icon_path:
            self.tray_icon.setIcon(QIcon(self.icon_path))
        else:
            self.tray_icon.setIcon(QIcon())

        # 创建托盘菜单
        tray_menu = QMenu()

        # 显示/隐藏主窗口动作
        self.toggle_window_action = QAction("显示主窗口", self)
        self.toggle_window_action.triggered.connect(self.toggle_main_window)
        tray_menu.addAction(self.toggle_window_action)

        # 显示状态动作
        status_action = QAction("显示状态", self)
        status_action.triggered.connect(self.show_status)
        tray_menu.addAction(status_action)

        tray_menu.addSeparator()

        # 启用通知动作
        self.notify_action = QAction("启用通知", self)
        self.notify_action.setCheckable(True)
        self.notify_action.triggered.connect(self.toggle_notifications_from_tray)
        tray_menu.addAction(self.notify_action)

        # 开机自启动动作
        self.startup_action = QAction("开机自启动", self)
        self.startup_action.setCheckable(True)
        self.startup_action.triggered.connect(self.toggle_auto_start_from_tray)
        tray_menu.addAction(self.startup_action)

        tray_menu.addSeparator()

        # 主题切换子菜单
        theme_menu = QMenu("主题设置")

        # 浅色主题动作
        light_theme_action = QAction("浅色", self)
        light_theme_action.triggered.connect(lambda: self.switch_theme("light"))
        theme_menu.addAction(light_theme_action)

        # 深色主题动作
        dark_theme_action = QAction("深色", self)
        dark_theme_action.triggered.connect(lambda: self.switch_theme("dark"))
        theme_menu.addAction(dark_theme_action)

        tray_menu.addMenu(theme_menu)

        tray_menu.addSeparator()

        # 打开配置目录动作
        config_dir_action = QAction("打开配置目录", self)
        config_dir_action.triggered.connect(self.open_config_dir)
        tray_menu.addAction(config_dir_action)

        # 检查更新动作
        check_update_action = QAction("检查更新", self)
        check_update_action.triggered.connect(self.check_update)
        tray_menu.addAction(check_update_action)

        tray_menu.addSeparator()

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

        tray_menu.addSeparator()

        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.confirm_exit)
        tray_menu.addAction(exit_action)

        # 初始更新托盘菜单项文本
        self.update_tray_menu_text()

    @pyqtSlot(str)
    def switch_theme(self, theme):
        """
        切换应用程序主题

        Args:
            theme: 主题类型，可以是 "light" 或 "dark"
        """
        if theme != self.current_theme:
            self.current_theme = theme

            # 保存主题设置到配置文件
            self.config_manager.theme = theme
            if self.config_manager.save_config():
                logger.debug(f"主题设置已保存到配置文件: {theme}")
            else:
                logger.warning(f"主题设置保存失败: {theme}")

            # 使用指定主题
            theme_manager.set_theme(theme)
            logger.debug(f"主题已设置为: {theme}")

            # 主题切换现在通过信号自动完成，只需要应用组件属性
            self.apply_component_properties()

    def apply_component_properties(self):
        """应用组件属性"""
        try:
            # 设置无边框窗口透明背景属性
            StyleHelper.set_frameless_window_properties(self)

            # 设置选项卡透明背景
            if hasattr(self, "tabs"):
                StyleHelper.set_tab_page_transparent(self.tabs)

            # 设置按钮类型属性
            self.setup_button_properties()

            # 设置标签类型属性
            self.setup_label_properties()

            # 重新绘制窗口以应用新主题
            self.update()

        except Exception as e:
            logger.error(f"应用组件属性失败: {str(e)}")

    def setup_button_properties(self):
        """设置按钮属性"""
        try:
            # 设置按钮
            if hasattr(self, "config_dir_btn"):
                StyleHelper.set_button_type(self.config_dir_btn, "default")
            if hasattr(self, "check_update_btn"):
                StyleHelper.set_button_type(self.check_update_btn, "default")
            if hasattr(self, "about_btn"):
                StyleHelper.set_button_type(self.about_btn, "default")

            # 主题切换按钮
            if hasattr(self, "light_theme_btn"):
                btn_type = "selected" if self.current_theme == "light" else "default"
                StyleHelper.set_button_type(self.light_theme_btn, btn_type)
            if hasattr(self, "dark_theme_btn"):
                btn_type = "selected" if self.current_theme == "dark" else "default"
                StyleHelper.set_button_type(self.dark_theme_btn, btn_type)

        except Exception as e:
            logger.error(f"设置按钮属性失败: {str(e)}")

    def setup_label_properties(self):
        """设置标签属性"""
        try:
            # 重新应用主题状态标签的样式
            if hasattr(self, "current_theme_label"):
                theme_name = "浅色" if self.current_theme == "light" else "深色"
                icon = "☀️" if self.current_theme == "light" else "🌙"
                status_text = f"{icon} 当前状态：{theme_name}主题"
                label_type = "success" if self.current_theme == "light" else "info"

                self.current_theme_label.setText(status_text)
                StyleHelper.set_label_type(self.current_theme_label, label_type)

        except Exception as e:
            logger.error(f"设置标签属性失败: {str(e)}")

    def _get_theme_display_name(self):
        """获取主题的显示名称"""
        if self.current_theme == "light":
            return "浅色"
        else:  # dark
            return "深色"

    def _toggle_notifications(self, from_tray=False):
        """通用通知切换方法"""
        if from_tray:
            self.config_manager.show_notifications = self.notify_action.isChecked()
            # 同步更新主窗口选项
            self.notify_checkbox.blockSignals(True)
            self.notify_checkbox.setChecked(self.config_manager.show_notifications)
            self.notify_checkbox.blockSignals(False)
        else:
            self.config_manager.show_notifications = self.notify_checkbox.isChecked()
            # 同步更新托盘菜单选项
            self.notify_action.blockSignals(True)
            self.notify_action.setChecked(self.config_manager.show_notifications)
            self.notify_action.blockSignals(False)

        # 保存配置
        if self.config_manager.save_config():
            logger.debug(f"通知状态已更改并保存: {'开启' if self.config_manager.show_notifications else '关闭'}")
        else:
            logger.warning(f"通知状态已更改但保存失败: {'开启' if self.config_manager.show_notifications else '关闭'}")

    def toggle_notifications(self):
        """切换通知开关"""
        self._toggle_notifications(from_tray=False)

    def toggle_notifications_from_tray(self):
        """从托盘菜单切换通知开关"""
        self._toggle_notifications(from_tray=True)

    def _toggle_auto_start(self, from_tray=False):
        """通用自启动切换方法"""
        if from_tray:
            self.config_manager.auto_start = self.startup_action.isChecked()
            # 同步更新主窗口选项
            self.startup_checkbox.blockSignals(True)
            self.startup_checkbox.setChecked(self.config_manager.auto_start)
            self.startup_checkbox.blockSignals(False)
        else:
            self.config_manager.auto_start = self.startup_checkbox.isChecked()
            # 同步更新托盘菜单选项
            self.startup_action.blockSignals(True)
            self.startup_action.setChecked(self.config_manager.auto_start)
            self.startup_action.blockSignals(False)

        # 修改注册表
        if self.config_manager.auto_start:
            enable_auto_start(self.app_name)
        else:
            disable_auto_start(self.app_name)

        # 保存配置
        if self.config_manager.save_config():
            logger.debug(f"开机自启状态已更改并保存: {'开启' if self.config_manager.auto_start else '关闭'}")
        else:
            logger.warning(f"开机自启状态已更改但保存失败: {'开启' if self.config_manager.auto_start else '关闭'}")

    def toggle_auto_start(self):
        """切换开机自启动开关"""
        self._toggle_auto_start(from_tray=False)

    def toggle_auto_start_from_tray(self):
        """从托盘菜单切换开机自启动开关"""
        self._toggle_auto_start(from_tray=True)

    def open_config_dir(self):
        """打开配置目录"""
        try:
            if os.path.exists(self.config_manager.config_dir):
                if sys.platform == "win32":
                    os.startfile(self.config_manager.config_dir)
                else:
                    import subprocess

                    subprocess.Popen(["xdg-open", self.config_manager.config_dir])
                logger.debug(f"已打开配置目录: {self.config_manager.config_dir}")
            else:
                os.makedirs(self.config_manager.config_dir, exist_ok=True)
                if sys.platform == "win32":
                    os.startfile(self.config_manager.config_dir)
                else:
                    import subprocess

                    subprocess.Popen(["xdg-open", self.config_manager.config_dir])
                logger.debug(f"已创建并打开配置目录: {self.config_manager.config_dir}")
        except Exception as e:
            logger.error(f"打开配置目录失败: {str(e)}")
            QMessageBox.warning(self, "错误", f"打开配置目录失败: {str(e)}")

    def check_update(self):
        """检查更新"""
        # 显示正在检查的消息
        self.check_update_btn.setText("检查中...")
        self.check_update_btn.setEnabled(False)

        # 异步检查更新
        self.version_checker.check_for_updates_async()

    def _open_download_url(self, download_url=None, is_direct_download=False):
        """
        打开下载链接或发布页面

        Args:
            download_url: 下载链接，如果为None则使用GitHub发布页面
            is_direct_download: 是否为直接下载链接
        """
        try:
            import webbrowser
            import os

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
            QMessageBox.warning(self, "错误", f"打开下载链接失败: {str(e)}")
            return False

    def _open_download_page(self, link):
        """
        通过版本标签链接触发下载

        Args:
            link: 链接文本
        """
        if hasattr(self, "download_url") and self.download_url:
            self._open_download_url(self.download_url, is_direct_download=True)
        else:
            self._open_download_url(self.github_releases_url, is_direct_download=False)

    @pyqtSlot(bool, str, str, str, str)
    def _on_version_check_finished(self, has_update, current_ver, latest_ver, update_info_str, error_msg):
        """版本检查完成的处理函数"""
        # 恢复按钮状态
        self.check_update_btn.setText("检查更新")
        self.check_update_btn.setEnabled(True)

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
        if has_update and latest_ver:
            # 添加HTML链接，设置为可点击状态
            self.version_label.setText(
                f"当前版本: v{current_ver} | 🆕 <b>最新版本: v{latest_ver} </b> <a href='#download' style='color: #28C940; font-weight: bold; font-size: 14px; text-decoration: none;'> 👉 前往下载</a>"
            )
            self.version_label.setOpenExternalLinks(False)  # 使用自定义逻辑来处理链接
            self.version_label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
            # 连接到下载函数
            self.version_label.linkActivated.connect(self._open_download_page)
            StyleHelper.set_label_type(self.version_label, "warning")
        else:
            self.version_label.setText(f"当前版本: v{current_ver}")
            StyleHelper.set_label_type(self.version_label, "info")

        # 如果是静默模式，只更新界面不显示弹窗
        if silent_mode:
            logger.debug(f"静默检查更新中，有更新: {has_update}")
            # 如果有更新，在托盘图标中显示简短提示
            if has_update and self.config_manager.show_notifications:
                self.tray_icon.showMessage(
                    self.app_name,
                    f"发现新版本 v{latest_ver} 可用",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000,  # 显示3秒
                )
            return

        # 创建并显示消息
        result = create_update_message(
            has_update, current_ver, latest_ver, update_info_str, error_msg, self.github_releases_url
        )

        # 解包结果
        title, message, msg_type, extra_data = result

        import webbrowser

        if msg_type == "error":
            # 其他错误消息，询问是否手动访问GitHub
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)

            # 添加自定义按钮
            get_version_btn = msg_box.addButton("🌐 前往下载页面", QMessageBox.ButtonRole.YesRole)
            cancel_btn = msg_box.addButton("❌ 关闭", QMessageBox.ButtonRole.NoRole)
            msg_box.setDefaultButton(cancel_btn)

            msg_box.exec()
            if msg_box.clickedButton() == get_version_btn:
                github_url = extra_data.get("github_url", self.github_releases_url)
                webbrowser.open(github_url)

        elif msg_type == "update":
            # 有新版本，询问是否前往下载
            msg_box = QMessageBox(self)
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
            if should_download:
                self._open_download_url(download_url, is_direct_download)

        else:
            QMessageBox.information(self, title, message)

    def show_about(self):
        """显示关于对话框"""
        # 创建自定义消息框，添加访问官网的选项
        msg_box = QMessageBox(self)
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
            import webbrowser

            github_url = f"https://github.com/{self.github_repo}"
            webbrowser.open(github_url)
            logger.debug("用户通过关于对话框访问了项目官网")

    def toggle_main_window(self):
        """切换主窗口的显示状态"""
        if self.isHidden() or self.is_custom_minimized:
            # 如果窗口隐藏或是自定义最小化状态，则显示窗口
            if self.is_custom_minimized:
                self.restore_from_custom_minimize()
            else:
                self.showNormal()
                self.activateWindow()
            logger.debug("从托盘菜单显示主窗口")
        else:
            # 如果窗口已显示，则最小化到托盘
            if hasattr(self, "custom_titlebar") and self.custom_titlebar:
                self.custom_titlebar.minimize_to_tray()
                logger.debug("从托盘菜单隐藏主窗口到托盘")
            else:
                self.hide()
                logger.debug("从托盘菜单隐藏主窗口")

        self.update_tray_menu_text()

    def update_tray_menu_text(self):
        """更新托盘菜单项文本"""
        if hasattr(self, "toggle_window_action"):
            if self.isHidden() or self.is_custom_minimized:
                self.toggle_window_action.setText("显示主窗口")
            else:
                self.toggle_window_action.setText("隐藏窗口到托盘")

    def restore_from_custom_minimize(self):
        """从自定义标题栏最小化状态恢复窗口"""
        if hasattr(self, "custom_titlebar") and self.custom_titlebar:
            self.custom_titlebar.safe_restore_window()
            logger.debug("使用safe_restore_window()方法恢复窗口")
        else:
            # 否则使用简单恢复
            self.setWindowOpacity(1.0)
            self.show()
            self.showNormal()
            self.activateWindow()
            self.is_custom_minimized = False
            logger.debug("主窗口已恢复")

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
        """处理托盘图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_main_window()

    def confirm_exit(self):
        """确认退出程序"""
        self.exit_app()

    def exit_app(self):
        """退出应用程序"""
        # 停止定时器（在主线程中处理）
        if hasattr(self, "update_timer") and self.update_timer:
            self.update_timer.stop()

        # 隐藏托盘图标（在主线程中处理）
        if hasattr(self, "tray_icon") and self.tray_icon:
            self.tray_icon.hide()

        # 退出应用
        QApplication.quit()

    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 根据配置设置执行相应操作
        if self.config_manager.close_to_tray:
            # 最小化到后台
            event.ignore()
            self.hide()
            self.update_tray_menu_text()
            # 如果托盘图标可见且通知开启，显示最小化提示
            if hasattr(self, "tray_icon") and self.tray_icon.isVisible() and self.config_manager.show_notifications:
                self.tray_icon.showMessage(
                    self.app_name,
                    "程序已最小化到系统托盘，继续在后台运行",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000,
                )
        else:
            # 直接退出程序
            event.accept()
            self.exit_app()

    def toggle_debug_mode(self):
        """切换调试模式"""
        # 获取新的调试模式状态
        new_debug_mode = self.debug_checkbox.isChecked()
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
        close_to_tray = self.close_behavior_combo.currentData()
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
            # 获取当前复选框状态
            check_update_on_start = self.check_update_on_start_checkbox.isChecked()

            # 更新配置
            self.config_manager.check_update_on_start = check_update_on_start

            # 保存配置
            if self.config_manager.save_config():
                logger.debug(f"启动时检查更新设置已保存: {check_update_on_start}")
            else:
                logger.warning("启动时检查更新设置保存失败")

        except Exception as e:
            logger.error(f"切换启动时检查更新设置失败: {str(e)}")
            QMessageBox.warning(self, "错误", f"切换启动时检查更新设置失败: {str(e)}")

            # 恢复界面状态
            self.check_update_on_start_checkbox.setChecked(self.config_manager.check_update_on_start)


def get_start_type_display(start_type):
    """获取启动类型的显示名称"""
    if start_type == "auto":
        return "自动启动"
    elif start_type == "disabled":
        return "已禁用"
    elif start_type == "manual":
        return "手动"
    elif start_type == "boot":
        return "系统启动"
    elif start_type == "system":
        return "系统"
    else:
        return start_type


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
