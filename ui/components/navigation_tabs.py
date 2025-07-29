#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
导航选项卡组件

专门用于左侧垂直导航的选项卡组件，支持图标和文本显示。
包含三个预设选项：猫咪设置、通用设置、模型管理。
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from ui.styles import AntColors, AntColorsDark, theme_manager


class NavigationButton(QPushButton):
    """导航按钮组件"""

    def __init__(self, text: str, icon_text: str = "", parent=None):
        super().__init__(parent)
        self.text_content = text
        self.icon_text = icon_text
        self.is_active = False

        self.setCheckable(True)
        self.setFixedHeight(56)
        self.setMinimumWidth(140)

        # 设置布局
        self._setup_layout()

        # 应用样式
        self._update_style()

        # 监听主题变化
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_layout(self):
        """设置按钮布局"""
        # 创建水平布局
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # 图标标签
        self.icon_label = QLabel(self.icon_text)
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        # 文本标签
        self.text_label = QLabel(self.text_content)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        font = QFont()
        font.setPointSize(13)
        font.setWeight(QFont.Weight.Medium)
        self.text_label.setFont(font)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addStretch()

        self.setLayout(layout)

    def setActive(self, active: bool):
        """设置激活状态"""
        self.is_active = active
        self.setChecked(active)
        self._update_style()

    def _update_style(self):
        """更新样式"""
        colors = AntColorsDark if theme_manager.is_dark_theme() else AntColors

        if self.is_active:
            # 激活状态样式
            bg_color = colors.PRIMARY_1
            text_color = colors.PRIMARY_6
            icon_color = colors.PRIMARY_6
            border_color = colors.PRIMARY_3

            style = f"""
                NavigationButton {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                    text-align: left;
                    font-weight: 600;
                }}
                NavigationButton:hover {{
                    background-color: {colors.PRIMARY_2};
                    border-color: {colors.PRIMARY_4};
                }}
                NavigationButton:pressed {{
                    background-color: {colors.PRIMARY_3};
                }}
            """
        else:
            # 未激活状态样式
            bg_color = "transparent"
            text_color = colors.GRAY_9
            icon_color = colors.GRAY_7

            style = f"""
                NavigationButton {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                }}
                NavigationButton:hover {{
                    background-color: {colors.GRAY_3};
                }}
                NavigationButton:pressed {{
                    background-color: {colors.GRAY_4};
                }}
            """

        self.setStyleSheet(style)

        # 更新图标和文本颜色
        if hasattr(self, "icon_label"):
            self.icon_label.setStyleSheet(f"color: {icon_color}; font-size: 16px; font-weight: bold;")
        if hasattr(self, "text_label"):
            self.text_label.setStyleSheet(f"color: {text_color};")

    def _on_theme_changed(self, theme):
        """主题变化时更新样式"""
        self._update_style()


class NavigationTabs(QWidget):
    """导航选项卡组件"""

    # 信号：当前选项卡改变
    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_index = 0
        self.buttons = []

        self._setup_ui()
        self._setup_navigation_items()

        # 设置默认激活项
        self.setCurrentIndex(0)

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # 导航按钮容器
        self.nav_container = QVBoxLayout()
        self.nav_container.setSpacing(4)

        layout.addLayout(self.nav_container)
        layout.addStretch()

        self.setLayout(layout)

        # 设置固定宽度
        self.setFixedWidth(160)

        # 应用背景样式
        colors = AntColorsDark if theme_manager.is_dark_theme() else AntColors
        self.setStyleSheet(
            f"""
            NavigationTabs {{
                background-color: {colors.GRAY_1};
                border-right: 1px solid {colors.GRAY_4};
            }}
        """
        )

    def _setup_navigation_items(self):
        """设置导航项目"""
        # 导航项目配置
        nav_items = [("猫咪设置", "🐱"), ("通用设置", "⚙️"), ("模型管理", "🔧")]

        for i, (text, icon) in enumerate(nav_items):
            button = NavigationButton(text, icon)
            button.clicked.connect(lambda checked, idx=i: self._on_button_clicked(idx))

            self.buttons.append(button)
            self.nav_container.addWidget(button)

    def _on_button_clicked(self, index: int):
        """处理按钮点击"""
        if index != self.current_index:
            self.setCurrentIndex(index)

    def setCurrentIndex(self, index: int):
        """设置当前选中的索引"""
        if 0 <= index < len(self.buttons):
            # 更新之前的按钮状态
            if 0 <= self.current_index < len(self.buttons):
                self.buttons[self.current_index].setActive(False)

            # 更新当前按钮状态
            self.current_index = index
            self.buttons[index].setActive(True)

            # 发送信号
            self.currentChanged.emit(index)

    def currentIndex(self) -> int:
        """获取当前选中的索引"""
        return self.current_index

    def addTab(self, text: str, icon_text: str = ""):
        """添加新的选项卡"""
        button = NavigationButton(text, icon_text)
        button.clicked.connect(lambda checked, idx=len(self.buttons): self._on_button_clicked(idx))

        self.buttons.append(button)
        self.nav_container.addWidget(button)

    def setTabText(self, index: int, text: str):
        """设置选项卡文本"""
        if 0 <= index < len(self.buttons):
            self.buttons[index].text_label.setText(text)

    def tabText(self, index: int) -> str:
        """获取选项卡文本"""
        if 0 <= index < len(self.buttons):
            return self.buttons[index].text_label.text()
        return ""


class NavigationTabWidget(QWidget):
    """完整的导航选项卡组件，包含选项卡和内容区域"""

    # 信号：当前选项卡改变
    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 左侧导航选项卡
        self.nav_tabs = NavigationTabs()
        self.nav_tabs.currentChanged.connect(self._on_current_changed)

        # 右侧内容区域
        self.content_stack = QStackedWidget()

        # 设置内容区域样式
        colors = AntColorsDark if theme_manager.is_dark_theme() else AntColors
        self.content_stack.setStyleSheet(
            f"""
            QStackedWidget {{
                background-color: {colors.GRAY_1};
                border-radius: 8px;
            }}
        """
        )

        layout.addWidget(self.nav_tabs)
        layout.addWidget(self.content_stack, 1)

        self.setLayout(layout)

    def _on_current_changed(self, index: int):
        """处理当前选项卡改变"""
        self.content_stack.setCurrentIndex(index)
        self.currentChanged.emit(index)

    def addTab(self, widget: QWidget, text: str, icon_text: str = ""):
        """添加选项卡"""
        self.nav_tabs.addTab(text, icon_text)
        self.content_stack.addWidget(widget)

    def setCurrentIndex(self, index: int):
        """设置当前选中的索引"""
        self.nav_tabs.setCurrentIndex(index)

    def currentIndex(self) -> int:
        """获取当前选中的索引"""
        return self.nav_tabs.currentIndex()

    def widget(self, index: int) -> QWidget:
        """获取指定索引的内容组件"""
        return self.content_stack.widget(index)

    def count(self) -> int:
        """获取选项卡数量"""
        return self.content_stack.count()
