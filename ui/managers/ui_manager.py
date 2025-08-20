#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""UI组件管理器"""

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QWidget,
    QComboBox,
    QFrame,
)
from PyQt5.QtCore import Qt
from ui.styles import StyleHelper, TitleHelper
from ui.components.modern_switch import ModernSwitch
from ui.components.card_group_box import CardGroupBox
from app.components.custom_grips import CustomGrip
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

        # 创建选项卡 - 使用重构后的导航选项卡组件
        from ui.components.navigation_tabs import NavigationTabWidget

        self.main_window.tabs = NavigationTabWidget()

        # 添加窗口边缘拖拽调整大小功能
        self._setup_window_grips()

        # 设置Logo - 使用favicon.ico
        import os

        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icon", "tray.png"
        )
        self.main_window.tabs.setLogo(icon_path=icon_path, logo_text=self.main_window.app_name)

        content_layout.addWidget(self.main_window.tabs)

        # 添加窗口边缘拖拽调整大小功能
        self._setup_window_grips()

        return content_layout

    def _setup_window_grips(self):
        """设置窗口边缘拖拽调整大小功能"""
        # 创建四个边缘的拖拽控件，禁用颜色显示（透明）
        self.main_window.left_grip = CustomGrip(self.main_window, Qt.LeftEdge, disable_color=True)
        self.main_window.right_grip = CustomGrip(self.main_window, Qt.RightEdge, disable_color=True)
        self.main_window.top_grip = CustomGrip(self.main_window, Qt.TopEdge, disable_color=True)
        self.main_window.bottom_grip = CustomGrip(self.main_window, Qt.BottomEdge, disable_color=True)

        # 保存原始的resizeEvent方法（从QWidget类获取）
        from PyQt5.QtWidgets import QWidget
        self.main_window._original_resize_event = QWidget.resizeEvent

        # 重写窗口的resizeEvent方法
        self.main_window.resizeEvent = self._on_window_resize

        # 初始化拖拽区域位置
        self._update_grips_geometry()

    def _update_grips_geometry(self):
        """更新拖拽区域的几何位置"""
        if hasattr(self.main_window, 'left_grip'):
            # 更新左边缘拖拽区域（避开标题栏区域）
            self.main_window.left_grip.setGeometry(0, 35, 10, self.main_window.height() - 35)

            # 更新右边缘拖拽区域（避开标题栏区域）
            self.main_window.right_grip.setGeometry(
                self.main_window.width() - 10, 35, 10, self.main_window.height() - 35
            )

            # 更新顶部边缘拖拽区域（避开标题栏）
            self.main_window.top_grip.setGeometry(0, 0, self.main_window.width(), 10)

            # 更新底部边缘拖拽区域
            self.main_window.bottom_grip.setGeometry(
                0, self.main_window.height() - 10, self.main_window.width(), 10
            )

    def _on_window_resize(self, event):
        """窗口大小变化时调整拖拽区域位置"""
        # 更新拖拽区域几何位置
        self._update_grips_geometry()

        # 调用原始的resizeEvent方法
        if hasattr(self.main_window, '_original_resize_event'):
            self.main_window._original_resize_event(self.main_window, event)

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

        # 设置布局间距和边距，为卡片样式优化
        cat_layout.setContentsMargins(16, 16, 16, 16)  # 增加边距
        cat_layout.setSpacing(12)  # 设置卡片之间的间距

        # 标题 - 使用TitleHelper创建
        title_label = TitleHelper.create_section_title("🐱 猫咪设置")
        cat_layout.addWidget(title_label)

        # 猫咪配置组标题
        config_title = TitleHelper.create_card_title("猫咪配置")
        cat_layout.addWidget(config_title)

        # 猫咪配置组
        cat_config_group = CardGroupBox()
        cat_config_group.setHoverable(False)  # 禁用悬停效果

        # 这里可以添加猫咪相关的设置控件
        placeholder_label = QLabel(
            "猫咪设置功能正在开发中...\n\n这里将包含：\n• 猫咪信息管理\n• 喂食提醒设置\n• 健康记录\n• 照片管理"
        )
        placeholder_label.setStyleSheet("color: #666; padding: 20px; text-align: center;")
        cat_config_group.addWidget(placeholder_label)

        cat_layout.addWidget(cat_config_group)

        cat_layout.addStretch()

        # 添加选项卡
        self.main_window.tabs.addTab(cat_tab, "猫咪设置", "🐱")

    def create_general_settings_tab(self):
        """创建通用设置选项卡"""
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)

        # 设置布局间距和边距，为卡片样式优化
        settings_layout.setContentsMargins(16, 16, 16, 16)  # 增加边距
        settings_layout.setSpacing(12)  # 设置卡片之间的间距

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
        self.main_window.tabs.addTab(settings_tab, "通用设置", "⚙️")

    def create_model_management_tab(self):
        """创建模型管理选项卡"""
        model_tab = QWidget()
        model_layout = QVBoxLayout(model_tab)

        # 设置布局间距和边距，为卡片样式优化
        model_layout.setContentsMargins(16, 16, 16, 16)  # 增加边距
        model_layout.setSpacing(12)  # 设置卡片之间的间距

        # 标题 - 使用TitleHelper创建
        title_label = TitleHelper.create_section_title("🔧 模型管理")
        model_layout.addWidget(title_label)

        # 模型列表组标题
        model_list_title = TitleHelper.create_card_title("已安装的模型")
        model_layout.addWidget(model_list_title)

        # 模型列表组
        model_list_group = CardGroupBox()
        model_list_group.setHoverable(False)  # 禁用悬停效果

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
            model_list_group.addWidget(model_frame)

        model_layout.addWidget(model_list_group)

        # 操作按钮组标题
        actions_title = TitleHelper.create_card_title("操作")
        model_layout.addWidget(actions_title)

        # 操作按钮组
        actions_group = CardGroupBox()
        actions_group.setHoverable(False)  # 禁用悬停效果

        # 创建水平布局来放置按钮
        actions_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 刷新模型列表")
        install_btn = QPushButton("📥 安装新模型")
        settings_btn = QPushButton("⚙️ 模型设置")

        actions_layout.addWidget(refresh_btn)
        actions_layout.addWidget(install_btn)
        actions_layout.addWidget(settings_btn)
        actions_layout.addStretch()

        actions_group.addLayout(actions_layout)
        model_layout.addWidget(actions_group)

        model_layout.addStretch()

        # 添加选项卡
        self.main_window.tabs.addTab(model_tab, "模型管理", "🔧")

    def _create_notification_group(self, parent_layout):
        """创建通知设置组"""
        # 通知设置组标题
        notify_title = TitleHelper.create_card_title("通知设置")
        parent_layout.addWidget(notify_title)

        notify_group = CardGroupBox()
        notify_group.setHoverable(False)  # 禁用悬停效果

        # 创建水平布局来放置标签和开关
        notify_item_layout = QHBoxLayout()
        notify_label = QLabel("启用Windows通知")
        self.main_window.notify_checkbox = ModernSwitch()

        notify_item_layout.addWidget(notify_label)
        notify_item_layout.addStretch()
        notify_item_layout.addWidget(self.main_window.notify_checkbox)

        notify_group.addLayout(notify_item_layout)
        parent_layout.addWidget(notify_group)

    def _create_startup_group(self, parent_layout):
        """创建启动设置组"""
        # 启动设置组标题
        startup_title = TitleHelper.create_card_title("启动设置")
        parent_layout.addWidget(startup_title)

        startup_group = CardGroupBox()
        startup_group.setHoverable(False)  # 禁用悬停效果

        # 开机自启动设置
        startup_item_layout = QHBoxLayout()
        startup_label = QLabel("开机自启动")
        self.main_window.startup_checkbox = ModernSwitch()

        startup_item_layout.addWidget(startup_label)
        startup_item_layout.addStretch()
        startup_item_layout.addWidget(self.main_window.startup_checkbox)
        startup_group.addLayout(startup_item_layout)

        # 启动时检查更新设置
        update_item_layout = QHBoxLayout()
        update_label = QLabel("启动时检查更新")
        self.main_window.check_update_on_start_checkbox = ModernSwitch()

        update_item_layout.addWidget(update_label)
        update_item_layout.addStretch()
        update_item_layout.addWidget(self.main_window.check_update_on_start_checkbox)
        startup_group.addLayout(update_item_layout)

        parent_layout.addWidget(startup_group)

    def _create_window_behavior_group(self, parent_layout):
        """创建窗口行为设置组"""
        # 窗口行为设置组标题
        window_title = TitleHelper.create_card_title("窗口行为设置")
        parent_layout.addWidget(window_title)

        window_group = CardGroupBox()
        window_group.setHoverable(False)  # 禁用悬停效果

        # 关闭行为选择
        close_behavior_layout = QHBoxLayout()
        close_behavior_label = QLabel("关闭窗口时:")
        close_behavior_layout.addWidget(close_behavior_label)

        self.main_window.close_behavior_combo = QComboBox()
        self.main_window.close_behavior_combo.addItem("最小化到系统托盘", True)
        self.main_window.close_behavior_combo.addItem("直接退出程序", False)
        close_behavior_layout.addWidget(self.main_window.close_behavior_combo)

        close_behavior_layout.addStretch()
        window_group.addLayout(close_behavior_layout)

        # 添加说明文本
        close_behavior_info = QLabel("💡 最小化到系统托盘：程序将继续在后台运行\n💡 直接退出程序：完全关闭程序进程")
        close_behavior_info.setWordWrap(True)
        StyleHelper.set_label_type(close_behavior_info, "info")
        window_group.addWidget(close_behavior_info)

        parent_layout.addWidget(window_group)

    def _create_log_group(self, parent_layout):
        """创建日志设置组"""
        # 日志设置组标题
        log_title = TitleHelper.create_card_title("日志设置")
        parent_layout.addWidget(log_title)

        log_group = CardGroupBox()
        log_group.setHoverable(False)  # 禁用悬停效果

        # 调试模式设置
        debug_item_layout = QHBoxLayout()
        debug_label = QLabel("启用调试模式")
        self.main_window.debug_checkbox = ModernSwitch()

        debug_item_layout.addWidget(debug_label)
        debug_item_layout.addStretch()
        debug_item_layout.addWidget(self.main_window.debug_checkbox)
        log_group.addLayout(debug_item_layout)

        parent_layout.addWidget(log_group)

    def _create_theme_group(self, parent_layout):
        """创建主题设置组"""
        # 主题设置组标题
        theme_title = TitleHelper.create_card_title("主题设置")
        parent_layout.addWidget(theme_title)

        theme_group = CardGroupBox()
        theme_group.setHoverable(False)  # 禁用悬停效果

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

        theme_group.addLayout(theme_buttons_layout)
        parent_layout.addWidget(theme_group)

    def _create_actions_group(self, parent_layout):
        """创建操作按钮组"""
        # 操作按钮组标题
        actions_title = TitleHelper.create_card_title("操作")
        parent_layout.addWidget(actions_title)

        actions_group = CardGroupBox()
        actions_group.setHoverable(False)  # 禁用悬停效果

        # 创建水平布局来放置按钮
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

        actions_group.addLayout(actions_layout)
        parent_layout.addWidget(actions_group)

    def _create_version_group(self, parent_layout):
        """创建版本信息组"""
        # 版本信息组标题
        version_title = TitleHelper.create_card_title("版本信息")
        parent_layout.addWidget(version_title)

        version_group = CardGroupBox()
        version_group.setHoverable(False)  # 禁用悬停效果

        # 获取当前版本号
        current_version = get_app_version(self.config_manager)
        self.main_window.version_label = QLabel(f"当前版本: v{current_version}")
        self.main_window.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        StyleHelper.set_label_type(self.main_window.version_label, "info")
        version_group.addWidget(self.main_window.version_label)

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
