#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
导航选项卡组件

专门用于左侧垂直导航的选项卡组件，支持图标和文本显示
内容区域支持自动滚动，当内容超出可用高度时显示垂直滚动条

NavigationTabWidget 结构:
├── NavigationTabs   # 左侧导航按钮
└── QStackedWidget   # 右侧内容区域
    └── QScrollArea  # 滚动包装器（自动添加）
        └── QWidget  # 用户内容

特性:
- 垂直滚动条仅在需要时显示
- 水平滚动条始终隐藏
- 保持现有布局和样式
- 支持主题切换

"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QFrame,
    QScrollArea,
    QGraphicsOpacityEffect,
)
from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
    QSize,
    QPropertyAnimation,
    QEasingCurve,
    QRect,
    pyqtProperty,
    QParallelAnimationGroup,
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from ui.styles import AntColors, AntColorsDark, theme_manager


class NavigationButton(QPushButton):
    """导航按钮组件 - 带有Fluent Design风格的指示器和动画效果"""

    def __init__(self, text: str, icon_text: str = "", parent=None):
        super().__init__(parent)
        self.text_content = text
        self.icon_text = icon_text
        self.is_active = False

        # 动画属性
        self._indicator_position = -6.0  # 指示器X坐标（初始在左边界外）
        self._indicator_opacity = 0.0  # 指示器透明度

        # 动画对象
        self._animation_group = None
        self._indicator_pos_animation = None
        self._indicator_opacity_animation = None

        self.setCheckable(True)
        self.setFixedHeight(56)
        self.setMinimumWidth(140)

        # 设置布局
        self._setup_layout()

        # 初始化动画
        self._setup_animations()

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

    def _setup_animations(self):
        """初始化动画"""
        # 创建动画组
        self._animation_group = QParallelAnimationGroup(self)

        # 指示器位置动画
        self._indicator_pos_animation = QPropertyAnimation(self, b"indicatorPosition")
        self._indicator_pos_animation.setDuration(250)
        self._indicator_pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 指示器透明度动画
        self._indicator_opacity_animation = QPropertyAnimation(self, b"indicatorOpacity")
        self._indicator_opacity_animation.setDuration(200)
        self._indicator_opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 添加到动画组
        self._animation_group.addAnimation(self._indicator_pos_animation)
        self._animation_group.addAnimation(self._indicator_opacity_animation)

    # 动画属性定义
    @pyqtProperty(float)
    def indicatorPosition(self):
        return self._indicator_position

    @indicatorPosition.setter
    def indicatorPosition(self, value):
        if abs(self._indicator_position - value) > 0.01:  # 只有变化足够大时才更新
            self._indicator_position = value
            # 使用QTimer.singleShot来避免在paintEvent中直接调用update()
            from PyQt6.QtCore import QTimer

            QTimer.singleShot(0, self.update)

    @pyqtProperty(float)
    def indicatorOpacity(self):
        return self._indicator_opacity

    @indicatorOpacity.setter
    def indicatorOpacity(self, value):
        # 限制透明度范围并检查变化
        new_value = max(0.0, min(1.0, value))
        if abs(self._indicator_opacity - new_value) > 0.01:  # 只有变化足够大时才更新
            self._indicator_opacity = new_value
            # 使用QTimer.singleShot来避免在paintEvent中直接调用update()
            from PyQt6.QtCore import QTimer

            QTimer.singleShot(0, self.update)

    def setActive(self, active: bool):
        """设置激活状态并触发动画"""
        if self.is_active == active:
            return  # 状态没有改变，不需要动画

        self.is_active = active
        self.setChecked(active)
        self._update_style()

        # 启动动画
        self._start_activation_animation(active)

    def _start_activation_animation(self, active: bool):
        """启动激活/非激活动画"""
        # 停止当前动画
        if self._animation_group.state() == QPropertyAnimation.State.Running:
            self._animation_group.stop()

        if active:
            # 激活动画：指示器滑入
            self._indicator_pos_animation.setStartValue(self._indicator_position)
            self._indicator_pos_animation.setEndValue(1.0)  # 滑入到正确位置

            self._indicator_opacity_animation.setStartValue(self._indicator_opacity)
            self._indicator_opacity_animation.setEndValue(1.0)  # 完全不透明
        else:
            # 非激活动画：指示器滑出
            self._indicator_pos_animation.setStartValue(self._indicator_position)
            self._indicator_pos_animation.setEndValue(-6.0)  # 滑出到左边界外

            self._indicator_opacity_animation.setStartValue(self._indicator_opacity)
            self._indicator_opacity_animation.setEndValue(0.0)  # 完全透明

        # 启动动画组
        self._animation_group.start()

    def _update_style(self):
        """更新样式"""
        # 使用 setProperty 设置按钮状态，让 styles.py 中的样式自动应用
        if self.is_active:
            self.setProperty("buttonState", "active")
        else:
            self.setProperty("buttonState", "inactive")

        # 刷新样式以应用新的属性
        self.style().unpolish(self)
        self.style().polish(self)

        # 更新内部标签的颜色（这些不在全局样式中定义）
        colors = AntColorsDark if theme_manager.is_dark_theme() else AntColors

        if self.is_active:
            icon_color = colors.PRIMARY_6
            text_color = colors.PRIMARY_6
        else:
            icon_color = colors.GRAY_7
            text_color = colors.GRAY_9

        # 只设置图标和文本的颜色，其他样式由 styles.py 管理
        if hasattr(self, "icon_label"):
            self.icon_label.setStyleSheet(f"color: {icon_color}; font-size: 16px; font-weight: bold;")
        if hasattr(self, "text_label"):
            self.text_label.setStyleSheet(f"color: {text_color}; ")

    def _on_theme_changed(self, theme):
        """主题变化时更新样式"""
        self._update_style()

    def paintEvent(self, event):
        """自定义绘制事件 - 添加带动画的Fluent Design风格圆滑指示器"""
        # 调用父类绘制方法（让CSS样式正常工作）
        super().paintEvent(event)

        # 绘制指示器（如果透明度大于0）
        if self._indicator_opacity > 0.0:
            self._draw_indicator()

    def _draw_indicator(self):
        """绘制指示器的独立方法"""
        # 检查widget是否有效
        if not self.isVisible() or self.width() <= 0 or self.height() <= 0:
            return

        painter = QPainter()

        # 检查是否能成功开始绘制
        if not painter.begin(self):
            return  # 如果无法开始绘制，直接返回

        try:
            # 设置抗锯齿
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

            # 获取当前主题颜色
            colors = AntColorsDark if theme_manager.is_dark_theme() else AntColors

            # 绘制左侧圆滑指示条
            indicator_width = 4
            indicator_height = min(28, self.height() - 4)  # 确保指示器不超出按钮高度
            indicator_x = max(0, min(self._indicator_position, self.width() - indicator_width))  # 限制位置范围
            indicator_y = (self.height() - indicator_height) // 2

            # 只有在有效区域内才绘制
            if indicator_height > 0 and indicator_x >= 0:
                # 设置指示器颜色和画笔
                indicator_color = QColor(colors.PRIMARY_6)
                indicator_color.setAlphaF(max(0.0, min(1.0, self._indicator_opacity)))  # 限制透明度范围
                painter.setBrush(indicator_color)
                painter.setPen(Qt.PenStyle.NoPen)

                # 绘制圆角矩形指示器
                from PyQt6.QtCore import QRectF

                indicator_rect = QRectF(indicator_x, indicator_y, indicator_width, indicator_height)
                corner_radius = indicator_width / 2
                painter.drawRoundedRect(indicator_rect, corner_radius, corner_radius)

        except Exception as e:
            # 如果绘制过程中出现异常，记录但不中断程序
            print(f"Warning: Error in indicator drawing: {e}")
        finally:
            # 确保painter正确结束
            if painter.isActive():
                painter.end()


class NavigationTabs(QWidget):
    """导航选项卡组件"""

    # 信号：当前选项卡改变
    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_index = 0
        self.buttons = []

        self._setup_ui()

        # 监听主题变化
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 8, 8, 8)
        layout.setSpacing(4)

        # 导航按钮容器
        self.nav_container = QVBoxLayout()
        self.nav_container.setSpacing(4)

        layout.addLayout(self.nav_container)
        layout.addStretch()

        self.setLayout(layout)

        # 设置固定宽度
        self.setFixedWidth(160)

        # 设置导航类型属性，让 styles.py 中的样式自动应用
        self.setProperty("navType", "vertical")

        # 刷新样式
        self.style().unpolish(self)
        self.style().polish(self)

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

        # 如果这是第一个选项卡，自动设置为激活状态
        if len(self.buttons) == 1:
            self.setCurrentIndex(0)

    def setTabText(self, index: int, text: str):
        """设置选项卡文本"""
        if 0 <= index < len(self.buttons):
            self.buttons[index].text_label.setText(text)

    def tabText(self, index: int) -> str:
        """获取选项卡文本"""
        if 0 <= index < len(self.buttons):
            return self.buttons[index].text_label.text()
        return ""

    def _on_theme_changed(self, theme):
        """主题变化时刷新样式"""
        # 刷新容器样式
        self.style().unpolish(self)
        self.style().polish(self)

        # 刷新所有按钮的样式（按钮有自己的主题变化处理）
        for button in self.buttons:
            button._update_style()


class NavigationTabWidget(QWidget):
    """完整的导航选项卡组件，包含选项卡和内容区域，支持动画切换"""

    # 信号：当前选项卡改变
    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        # 内容切换动画属性
        self._content_opacity = 1.0
        self._content_animation = None
        self._pending_index = -1  # 待切换的索引

        self._setup_ui()
        self._setup_content_animation()

        # 监听主题变化
        theme_manager.theme_changed.connect(self._on_theme_changed)

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

        # 设置内容区域属性，让 styles.py 中的样式自动应用
        self.content_stack.setProperty("contentType", "navigation")

        # 刷新样式
        self.content_stack.style().unpolish(self.content_stack)
        self.content_stack.style().polish(self.content_stack)

        layout.addWidget(self.nav_tabs)
        layout.addWidget(self.content_stack, 1)

        self.setLayout(layout)

    def _setup_content_animation(self):
        """设置内容切换动画"""
        self._content_animation = QPropertyAnimation(self, b"contentOpacity")
        self._content_animation.setDuration(200)
        self._content_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._content_animation.finished.connect(self._on_fade_out_finished)

    # 内容透明度属性
    @pyqtProperty(float)
    def contentOpacity(self):
        return self._content_opacity

    @contentOpacity.setter
    def contentOpacity(self, value):
        # 限制透明度范围
        new_value = max(0.0, min(1.0, value))
        if abs(self._content_opacity - new_value) > 0.01:  # 只有变化足够大时才更新
            self._content_opacity = new_value
            # 设置内容区域的透明度效果
            if not hasattr(self.content_stack, "_opacity_effect") or self.content_stack._opacity_effect is None:
                self.content_stack._opacity_effect = QGraphicsOpacityEffect()
                self.content_stack.setGraphicsEffect(self.content_stack._opacity_effect)

            # 安全地设置透明度
            try:
                self.content_stack._opacity_effect.setOpacity(new_value)
            except Exception as e:
                print(f"Warning: Error setting content opacity: {e}")

    def _on_current_changed(self, index: int):
        """处理当前选项卡改变，带动画效果"""
        if index == self.content_stack.currentIndex():
            return  # 相同索引，不需要切换

        # 保存待切换的索引
        self._pending_index = index

        # 开始淡出动画
        if self._content_animation.state() == QPropertyAnimation.State.Running:
            self._content_animation.stop()

        self._content_animation.setStartValue(self._content_opacity)
        self._content_animation.setEndValue(0.0)
        self._content_animation.start()

    def _on_fade_out_finished(self):
        """淡出动画完成后的回调"""
        if self._pending_index >= 0:
            # 切换到新内容
            self.content_stack.setCurrentIndex(self._pending_index)
            self.currentChanged.emit(self._pending_index)

            # 开始淡入动画
            self._content_animation.setStartValue(0.0)
            self._content_animation.setEndValue(1.0)
            self._content_animation.start()

            self._pending_index = -1

    def addTab(self, widget: QWidget, text: str, icon_text: str = ""):
        """添加选项卡"""
        self.nav_tabs.addTab(text, icon_text)

        # 创建滚动区域包装器
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(widget)

        # 设置滚动区域属性，让 styles.py 中的样式自动应用
        scroll_area.setProperty("contentType", "navigation")

        # 刷新样式
        scroll_area.style().unpolish(scroll_area)
        scroll_area.style().polish(scroll_area)

        self.content_stack.addWidget(scroll_area)

    def setCurrentIndex(self, index: int):
        """设置当前选中的索引"""
        self.nav_tabs.setCurrentIndex(index)

    def currentIndex(self) -> int:
        """获取当前选中的索引"""
        return self.nav_tabs.currentIndex()

    def widget(self, index: int) -> QWidget:
        """获取指定索引的内容组件"""
        scroll_area = self.content_stack.widget(index)
        if isinstance(scroll_area, QScrollArea):
            return scroll_area.widget()
        return scroll_area

    def count(self) -> int:
        """获取选项卡数量"""
        return self.content_stack.count()

    def _on_theme_changed(self, theme):
        """主题变化时刷新样式"""
        # 刷新内容区域样式
        self.content_stack.style().unpolish(self.content_stack)
        self.content_stack.style().polish(self.content_stack)

        # 刷新所有滚动区域的样式
        for i in range(self.content_stack.count()):
            scroll_area = self.content_stack.widget(i)
            if isinstance(scroll_area, QScrollArea):
                scroll_area.style().unpolish(scroll_area)
                scroll_area.style().polish(scroll_area)
