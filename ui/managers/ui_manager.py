#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""UI组件管理器"""

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QCheckBox,
    QGroupBox,
    QTabWidget,
    QWidget,
    QComboBox,
    QFrame,
)
from PyQt6.QtCore import Qt
from ui.styles import StyleHelper
from utils import get_app_version


class UIManager:
    """UI组件管理器，负责创建和组织界面元素"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.config_manager = main_window.config_manager

    def setup_main_layout(self):
        """设置主布局"""
        # 创建主布局 - 直接在QWidget上
        main_layout = QVBoxLayout(self.main_window)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 添加自定义标题栏
        from ui.components.custom_titlebar import CustomTitleBar

        self.main_window.custom_titlebar = CustomTitleBar(self.main_window)
        main_layout.addWidget(self.main_window.custom_titlebar)

        # 创建内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(8, 0, 8, 8)
        main_layout.addWidget(content_widget)

        # 创建选项卡 - 使用自定义选项卡组件支持水平文本
        from ui.components.custom_tabbar import CustomTabWidget

        self.main_window.tabs = CustomTabWidget()
        # 设置选项卡位置为左侧
        StyleHelper.set_tab_position(self.main_window.tabs, "West")
        content_layout.addWidget(self.main_window.tabs)

        return content_layout

    def create_all_tabs(self):
        """创建所有选项卡"""
        # 创建猫咪设置选项卡
        self.create_cat_settings_tab()

        # 创建通用设置选项卡
        self.create_general_settings_tab()

        # 创建模型管理选项卡
        self.create_model_management_tab()

    def create_cat_settings_tab(self):
        """创建猫咪设置选项卡"""
        cat_tab = QWidget()
        cat_layout = QVBoxLayout(cat_tab)

        # 标题
        title_label = QLabel("🐱 猫咪设置")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 16px;")
        cat_layout.addWidget(title_label)

        # 猫咪配置组
        cat_config_group = QGroupBox("猫咪配置")
        cat_config_layout = QVBoxLayout()

        # 这里可以添加猫咪相关的设置控件
        placeholder_label = QLabel(
            "猫咪设置功能正在开发中...\n\n这里将包含：\n• 猫咪信息管理\n• 喂食提醒设置\n• 健康记录\n• 照片管理"
        )
        placeholder_label.setStyleSheet("color: #666; padding: 20px; text-align: center;")
        cat_config_layout.addWidget(placeholder_label)

        cat_config_group.setLayout(cat_config_layout)
        cat_layout.addWidget(cat_config_group)

        cat_layout.addStretch()

        # 添加选项卡
        self.main_window.tabs.addTab(cat_tab, "🐱 猫咪设置")

    def create_general_settings_tab(self):
        """创建通用设置选项卡（原设置选项卡的重命名版本）"""
        self.create_settings_tab()

        # 更新选项卡标题
        tab_count = self.main_window.tabs.count()
        if tab_count > 0:
            self.main_window.tabs.setTabText(tab_count - 1, "⚙️ 通用设置")

    def create_model_management_tab(self):
        """创建模型管理选项卡"""
        model_tab = QWidget()
        model_layout = QVBoxLayout(model_tab)

        # 标题
        title_label = QLabel("🔧 模型管理")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 16px;")
        model_layout.addWidget(title_label)

        # 模型列表组
        model_list_group = QGroupBox("已安装的模型")
        model_list_layout = QVBoxLayout()

        # 模拟一些模型
        models = [
            ("GPT-4 Turbo", "✅ 已激活", "#52c41a"),
            ("Claude-3 Sonnet", "⏸️ 暂停", "#faad14"),
            ("Gemini Pro", "✅ 已激活", "#52c41a"),
            ("LLaMA 2 70B", "❌ 未安装", "#f5222d"),
        ]

        for model_name, status, color in models:
            model_frame = QFrame()
            model_frame.setFrameStyle(QFrame.Shape.Box)
            model_frame.setStyleSheet(f"padding: 8px; margin: 4px; border-radius: 6px; border: 1px solid #d9d9d9;")

            model_item_layout = QHBoxLayout()
            model_label = QLabel(model_name)
            model_label.setStyleSheet("font-weight: 500; font-size: 13px;")

            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: {color}; font-weight: 500;")

            model_item_layout.addWidget(model_label)
            model_item_layout.addStretch()
            model_item_layout.addWidget(status_label)

            model_frame.setLayout(model_item_layout)
            model_list_layout.addWidget(model_frame)

        model_list_group.setLayout(model_list_layout)
        model_layout.addWidget(model_list_group)

        # 操作按钮组
        actions_group = QGroupBox("操作")
        actions_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 刷新模型列表")
        install_btn = QPushButton("📥 安装新模型")
        settings_btn = QPushButton("⚙️ 模型设置")

        actions_layout.addWidget(refresh_btn)
        actions_layout.addWidget(install_btn)
        actions_layout.addWidget(settings_btn)
        actions_layout.addStretch()

        actions_group.setLayout(actions_layout)
        model_layout.addWidget(actions_group)

        model_layout.addStretch()

        # 添加选项卡
        self.main_window.tabs.addTab(model_tab, "🔧 模型管理")

    def create_settings_tab(self):
        """创建设置选项卡"""
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)

        # 创建各个设置组
        self._create_notification_group(settings_layout)
        self._create_startup_group(settings_layout)
        self._create_window_behavior_group(settings_layout)
        self._create_log_group(settings_layout)
        self._create_theme_group(settings_layout)
        self._create_actions_group(settings_layout)
        self._create_version_group(settings_layout)

        # 添加空白占位
        settings_layout.addStretch()

        # 添加选项卡
        self.main_window.tabs.addTab(settings_tab, "  设置  ")

    def _create_notification_group(self, parent_layout):
        """创建通知设置组"""
        notify_group = QGroupBox("通知设置")
        notify_layout = QVBoxLayout()

        self.main_window.notify_checkbox = QCheckBox("启用Windows通知")
        notify_layout.addWidget(self.main_window.notify_checkbox)

        notify_group.setLayout(notify_layout)
        parent_layout.addWidget(notify_group)

    def _create_startup_group(self, parent_layout):
        """创建启动设置组"""
        startup_group = QGroupBox("启动设置")
        startup_layout = QVBoxLayout()

        self.main_window.startup_checkbox = QCheckBox("开机自启动")
        startup_layout.addWidget(self.main_window.startup_checkbox)

        self.main_window.check_update_on_start_checkbox = QCheckBox("启动时检查更新")
        startup_layout.addWidget(self.main_window.check_update_on_start_checkbox)

        startup_group.setLayout(startup_layout)
        parent_layout.addWidget(startup_group)

    def _create_window_behavior_group(self, parent_layout):
        """创建窗口行为设置组"""
        window_group = QGroupBox("窗口行为设置")
        window_layout = QVBoxLayout()

        # 关闭行为选择
        close_behavior_layout = QHBoxLayout()
        close_behavior_label = QLabel("关闭窗口时:")
        close_behavior_layout.addWidget(close_behavior_label)

        self.main_window.close_behavior_combo = QComboBox()
        self.main_window.close_behavior_combo.addItem("最小化到系统托盘", True)
        self.main_window.close_behavior_combo.addItem("直接退出程序", False)
        close_behavior_layout.addWidget(self.main_window.close_behavior_combo)

        close_behavior_layout.addStretch()
        window_layout.addLayout(close_behavior_layout)

        # 添加说明文本
        close_behavior_info = QLabel("💡 最小化到系统托盘：程序将继续在后台运行\n💡 直接退出程序：完全关闭程序进程")
        close_behavior_info.setWordWrap(True)
        StyleHelper.set_label_type(close_behavior_info, "info")
        window_layout.addWidget(close_behavior_info)

        window_group.setLayout(window_layout)
        parent_layout.addWidget(window_group)

    def _create_log_group(self, parent_layout):
        """创建日志设置组"""
        log_group = QGroupBox("日志设置")
        log_layout = QVBoxLayout()

        self.main_window.debug_checkbox = QCheckBox("启用调试模式")
        log_layout.addWidget(self.main_window.debug_checkbox)

        log_group.setLayout(log_layout)
        parent_layout.addWidget(log_group)

    def _create_theme_group(self, parent_layout):
        """创建主题设置组"""
        theme_group = QGroupBox("主题设置")
        theme_layout = QVBoxLayout()

        # 主题选择水平布局
        theme_buttons_layout = QHBoxLayout()
        theme_buttons_layout.setSpacing(8)

        # 浅色主题按钮
        self.main_window.light_theme_btn = QPushButton("☀️ 浅色模式")
        self.main_window.light_theme_btn.setToolTip("切换到浅色主题模式")
        self.main_window.light_theme_btn.setMinimumHeight(32)
        theme_buttons_layout.addWidget(self.main_window.light_theme_btn)

        # 深色主题按钮
        self.main_window.dark_theme_btn = QPushButton("🌙 深色模式")
        self.main_window.dark_theme_btn.setToolTip("切换到深色主题模式")
        self.main_window.dark_theme_btn.setMinimumHeight(32)
        theme_buttons_layout.addWidget(self.main_window.dark_theme_btn)

        theme_layout.addLayout(theme_buttons_layout)
        theme_group.setLayout(theme_layout)
        parent_layout.addWidget(theme_group)

    def _create_actions_group(self, parent_layout):
        """创建操作按钮组"""
        actions_group = QGroupBox("操作")
        actions_layout = QHBoxLayout()

        # 打开配置目录按钮
        self.main_window.config_dir_btn = QPushButton("打开配置目录")
        actions_layout.addWidget(self.main_window.config_dir_btn)

        # 检查更新按钮
        self.main_window.check_update_btn = QPushButton("检查更新")
        actions_layout.addWidget(self.main_window.check_update_btn)

        # 关于按钮
        self.main_window.about_btn = QPushButton("关于")
        actions_layout.addWidget(self.main_window.about_btn)

        actions_group.setLayout(actions_layout)
        parent_layout.addWidget(actions_group)

    def _create_version_group(self, parent_layout):
        """创建版本信息组"""
        version_group = QGroupBox("版本信息")
        version_layout = QVBoxLayout()

        # 获取当前版本号
        current_version = get_app_version(self.config_manager)
        self.main_window.version_label = QLabel(f"当前版本: v{current_version}")
        self.main_window.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        StyleHelper.set_label_type(self.main_window.version_label, "info")
        version_layout.addWidget(self.main_window.version_label)

        version_group.setLayout(version_layout)
        parent_layout.addWidget(version_group)

    def setup_button_properties(self, current_theme):
        """设置按钮属性"""
        try:
            # 设置普通按钮
            if hasattr(self.main_window, "config_dir_btn"):
                StyleHelper.set_button_type(self.main_window.config_dir_btn, "default")
            if hasattr(self.main_window, "check_update_btn"):
                StyleHelper.set_button_type(self.main_window.check_update_btn, "default")
            if hasattr(self.main_window, "about_btn"):
                StyleHelper.set_button_type(self.main_window.about_btn, "default")

            # 主题切换按钮
            if hasattr(self.main_window, "light_theme_btn"):
                btn_type = "selected" if current_theme == "light" else "default"
                StyleHelper.set_button_type(self.main_window.light_theme_btn, btn_type)
            if hasattr(self.main_window, "dark_theme_btn"):
                btn_type = "selected" if current_theme == "dark" else "default"
                StyleHelper.set_button_type(self.main_window.dark_theme_btn, btn_type)

        except Exception as e:
            from utils import logger

            logger.error(f"设置按钮属性失败: {str(e)}")
