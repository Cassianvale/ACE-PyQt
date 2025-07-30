#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""现代化卡片样式的QGroupBox组件"""

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QBrush, QPen
from ui.styles import theme_manager, AntColors, AntColorsDark
from utils import logger


class CardGroupBox(QGroupBox):
    """现代化卡片样式的QGroupBox组件

    特性：
    - 圆角边框设计
    - 悬停状态视觉反馈
    - 自动适配深色/浅色主题
    - 支持自定义背景色和边框色
    - 响应式布局
    - 专注于卡片容器功能，标题由外部QLabel管理
    """

    # 信号
    clicked = pyqtSignal()
    hovered = pyqtSignal(bool)  # True: 进入悬停, False: 离开悬停

    def __init__(self, parent=None):
        super().__init__(parent)

        # 基础属性
        self._is_hoverable = True
        self._is_clickable = False
        self._hover_state = False
        self._border_radius = 12
        self._padding = 16
        self._shadow_enabled = True

        # 主题相关属性
        self._current_theme = theme_manager.get_current_theme()
        self._colors = self._get_theme_colors()

        # 动画属性
        self._hover_opacity = 1.0
        self._animation = None

        # 初始化组件
        self._setup_ui()
        self._setup_animations()
        self._setup_shadow()
        self._connect_signals()

        # 设置初始样式
        self._update_style()

    def _get_theme_colors(self):
        """获取当前主题的颜色配置"""
        return AntColorsDark if self._current_theme == "dark" else AntColors

    def _setup_ui(self):
        """设置UI结构"""
        # 移除默认标题显示
        self.setTitle("")

        # 设置基础属性
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        # 创建主容器
        self._main_widget = QWidget(self)
        self._main_layout = QVBoxLayout(self._main_widget)
        self._main_layout.setContentsMargins(self._padding, self._padding, self._padding, self._padding)
        self._main_layout.setSpacing(12)

        # 设置主布局 - 直接使用卡片主体
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self._main_widget)

    def _setup_animations(self):
        """设置动画效果"""
        self._animation = QPropertyAnimation(self, b"hover_opacity")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _setup_shadow(self):
        """设置阴影效果"""
        if self._shadow_enabled:
            try:
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(12)
                shadow.setColor(QColor(0, 0, 0, 40))
                shadow.setOffset(0, 4)
                # 将阴影应用到整个CardGroupBox而不是内部widget
                self.setGraphicsEffect(shadow)
            except Exception as e:
                logger.warning(f"设置阴影效果失败: {e}")
                self._shadow_enabled = False

    def _connect_signals(self):
        """连接信号"""
        # 监听主题变化
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme):
        """主题变化处理"""
        self._current_theme = theme
        self._colors = self._get_theme_colors()
        self._update_style()
        self.update()

    def _update_style(self):
        """更新样式"""
        # 卡片主体样式
        card_bg = self._colors.GRAY_1
        card_border = self._colors.GRAY_4
        hover_bg = self._colors.GRAY_2 if self._is_hoverable else card_bg

        # 根据悬停状态动态设置背景色
        current_bg = hover_bg if (self._is_hoverable and self._hover_state) else card_bg
        current_border = self._colors.PRIMARY_4 if (self._is_hoverable and self._hover_state) else card_border

        style = f"""
        CardGroupBox {{
            background-color: transparent;
            border: none;
            margin: 0px;
            padding: 0px;
        }}

        CardGroupBox > QWidget {{
            background-color: {current_bg};
            border: 1px solid {current_border};
            border-radius: {self._border_radius}px;
        }}

        /* 只有主容器有背景，不影响特定UI组件 */
        CardGroupBox > QWidget {{
            background-color: {current_bg};
            border: 1px solid {current_border};
            border-radius: {self._border_radius}px;
        }}

        /* 确保容器内的布局容器背景透明，但不影响UI控件 */
        CardGroupBox QWidget[objectName=""] {{
            background-color: transparent;
        }}
        """

        self.setStyleSheet(style)

    def paintEvent(self, event):
        """自定义绘制事件"""
        # 让父类处理基础绘制
        super().paintEvent(event)

    def enterEvent(self, event):
        """鼠标进入事件"""
        if self._is_hoverable:
            self._hover_state = True
            self.hovered.emit(True)
            self._update_style()  # 重新应用样式以显示悬停效果

            if self._animation:
                self._animation.setStartValue(self._hover_opacity)
                self._animation.setEndValue(0.9)
                self._animation.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件"""
        if self._is_hoverable:
            self._hover_state = False
            self.hovered.emit(False)
            self._update_style()  # 重新应用样式以移除悬停效果

            if self._animation:
                self._animation.setStartValue(self._hover_opacity)
                self._animation.setEndValue(1.0)
                self._animation.start()

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton and self._is_clickable:
            self.clicked.emit()
        super().mousePressEvent(event)

    # 属性访问器
    def get_hover_opacity(self):
        return self._hover_opacity

    def set_hover_opacity(self, value):
        self._hover_opacity = value
        self.update()

    hover_opacity = pyqtProperty(float, get_hover_opacity, set_hover_opacity)

    # 公共方法
    def setHoverable(self, hoverable):
        """设置是否启用悬停效果"""
        self._is_hoverable = hoverable
        self._update_style()

    def isHoverable(self):
        """获取是否启用悬停效果"""
        return self._is_hoverable

    def setClickable(self, clickable):
        """设置是否可点击"""
        self._is_clickable = clickable
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def isClickable(self):
        """获取是否可点击"""
        return self._is_clickable

    def setBorderRadius(self, radius):
        """设置圆角半径"""
        self._border_radius = radius
        self._update_style()

    def borderRadius(self):
        """获取圆角半径"""
        return self._border_radius

    def setPadding(self, padding):
        """设置内边距"""
        self._padding = padding
        if hasattr(self, "_main_layout"):
            self._main_layout.setContentsMargins(padding, padding, padding, padding)

    def padding(self):
        """获取内边距"""
        return self._padding

    def setShadowEnabled(self, enabled):
        """设置是否启用阴影"""
        self._shadow_enabled = enabled
        if enabled:
            self._setup_shadow()
        else:
            # 移除阴影效果
            self.setGraphicsEffect(None)

    def isShadowEnabled(self):
        """获取是否启用阴影"""
        return self._shadow_enabled

    def addWidget(self, widget):
        """添加子组件到卡片内容区域"""
        if hasattr(self, "_main_layout"):
            self._main_layout.addWidget(widget)

    def addLayout(self, layout):
        """添加布局到卡片内容区域"""
        if hasattr(self, "_main_layout"):
            self._main_layout.addLayout(layout)

    def getContentLayout(self):
        """获取内容区域的布局"""
        return self._main_layout if hasattr(self, "_main_layout") else None
