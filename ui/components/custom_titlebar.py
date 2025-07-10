#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from dataclasses import dataclass
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt6.QtCore import (
    Qt,
    QSize,
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QRect,
    QRectF,
    QTimer,
)
from PyQt6.QtGui import QIcon, QPainter, QBrush, QColor, QPen, QPainterPath, QRegion
from .circle_button import CircleButton
from ui.styles import AntColors, AntColorsDark, theme_manager
from utils import logger


@dataclass
class TitleBarConfig:
    """TitleBar配置"""

    HEIGHT: int = 35
    MARGIN: tuple = (10, 2, 10, 2)
    SPACING: int = 5  # favicon与标题间隔
    FONT_SIZE: int = 15  # 标题文字大小
    BUTTON_SIZE: int = 20  # 右上角button大小
    ICON_SIZE: int = 12  # 右上角button内的icon大小
    FAVICON_SIZE: int = 20  # favicon图标大小

    # 按钮颜色配置
    COLORS = {
        "systray": ("#FFB6C1", "#E6E6FA"),
        "minimize": ("#28C940", "#28C940"),
        "close": ("#FF5F57", "#FF5F57"),
    }

    # 图标配置 - 使用相对路径，运行时会转换为绝对路径
    ICONS = {
        "systray": "assets/icon/systray.svg",
        "minimize": "assets/icon/minus.svg",
        "close": "assets/icon/cross.svg",
        "favicon": "assets/icon/favicon.ico",
    }


class CustomTitleBar(QWidget):
    def __init__(self, parent=None, show_systray=True, show_minimize=True, show_close=True):
        super().__init__(parent)
        self.parent_widget = parent
        self.config = TitleBarConfig()
        self._start_pos = None
        self._is_tracking = False
        self.minimize_animations = None
        self.taskbar_animation = None

        # 控制按钮显示
        self.show_systray = show_systray
        self.show_minimize = show_minimize
        self.show_close = show_close

        # 不在标题栏中创建托盘图标，使用主窗口的托盘图标
        self.tray_icon = getattr(parent, "tray_icon", None)

        self.setFixedHeight(self.config.HEIGHT)
        self.setAutoFillBackground(True)

        # 连接主题切换信号
        theme_manager.theme_changed.connect(self.update_parent_window)

        self.init_ui()

    def _get_icon_path(self, icon_key):
        """获取图标的绝对路径"""
        try:
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            icon_path = os.path.join(project_root, self.config.ICONS[icon_key])

            # 如果文件不存在，返回None
            if not os.path.exists(icon_path):
                logger.warning(f"图标文件不存在: {icon_path}")
                return None

            return icon_path
        except Exception as e:
            logger.error(f"获取图标路径失败: {e}")
            return None

    def init_ui(self):
        """初始化UI"""
        self._setup_layout()
        self._create_title()
        self._create_buttons()

        # 为父窗口设置重绘功能
        self.setup_parent_window()

    def setup_parent_window(self):
        """为父窗口设置重绘功能"""
        if not self.parent_widget:
            return

        # 为父窗口添加重绘方法
        if not hasattr(self.parent_widget, "_original_paintEvent"):
            self.parent_widget._original_paintEvent = self.parent_widget.paintEvent
            self.parent_widget.paintEvent = self._parent_paintEvent

        if not hasattr(self.parent_widget, "_original_showEvent"):
            self.parent_widget._original_showEvent = self.parent_widget.showEvent
            self.parent_widget.showEvent = self._parent_showEvent

        if not hasattr(self.parent_widget, "_original_resizeEvent"):
            self.parent_widget._original_resizeEvent = self.parent_widget.resizeEvent
            self.parent_widget.resizeEvent = self._parent_resizeEvent

    def _parent_paintEvent(self, event):
        """父窗口的绘制事件"""
        if not self.parent_widget:
            return

        # 先调用原始的paintEvent（如果有的话）
        if hasattr(self.parent_widget, "_original_paintEvent"):
            try:
                self.parent_widget._original_paintEvent(event)
            except:
                pass

        # 绘制圆角窗口背景
        painter = QPainter(self.parent_widget)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # 获取当前主题颜色
        colors = AntColorsDark if theme_manager.get_current_theme() == "dark" else AntColors

        # 绘制圆角背景
        painter.setBrush(QBrush(QColor(colors.GRAY_1)))
        painter.setPen(QPen(QColor(colors.GRAY_4), 1))

        path = QPainterPath()
        rect = self.parent_widget.rect().adjusted(1, 1, -1, -1)
        path.addRoundedRect(float(rect.x()), float(rect.y()), float(rect.width()), float(rect.height()), 12.0, 12.0)
        painter.drawPath(path)

    def _parent_showEvent(self, event):
        """父窗口的显示事件"""
        if not self.parent_widget:
            return

        # 先调用原始的showEvent（如果有的话）
        if hasattr(self.parent_widget, "_original_showEvent"):
            try:
                self.parent_widget._original_showEvent(event)
            except:
                pass

        # 应用圆角遮罩
        self.apply_rounded_mask()

    def _parent_resizeEvent(self, event):
        """父窗口的大小改变事件"""
        if not self.parent_widget:
            return

        # 先调用原始的resizeEvent（如果有的话）
        if hasattr(self.parent_widget, "_original_resizeEvent"):
            try:
                self.parent_widget._original_resizeEvent(event)
            except:
                pass

        # 延迟应用遮罩以确保窗口完全调整大小后再应用
        QTimer.singleShot(10, self.apply_rounded_mask)

    def apply_rounded_mask(self):
        """应用圆角遮罩到父窗口"""
        if not self.parent_widget:
            return

        try:
            # 创建圆角路径
            path = QPainterPath()
            rect = self.parent_widget.rect()
            path.addRoundedRect(float(rect.x()), float(rect.y()), float(rect.width()), float(rect.height()), 12.0, 12.0)

            # 应用遮罩
            region = QRegion(path.toFillPolygon().toPolygon())
            self.parent_widget.setMask(region)

        except Exception as e:
            logger.error(f"应用圆角遮罩失败: {str(e)}")

    def update_parent_window(self):
        """更新父窗口显示（主题切换时调用）"""
        if self.parent_widget:
            self.parent_widget.update()

    def _setup_layout(self):
        """设置布局"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(*self.config.MARGIN)
        self.layout.setSpacing(self.config.SPACING)

    def _create_title(self):
        """创建标题标签"""
        # 创建图标标签
        self.icon_label = QLabel()
        icon_path = self._get_icon_path("favicon")
        if icon_path:
            icon = QIcon(icon_path)
            pixmap = icon.pixmap(QSize(self.config.FAVICON_SIZE, self.config.FAVICON_SIZE))
            self.icon_label.setPixmap(pixmap)
        else:
            logger.warning("favicon图标未找到，跳过图标显示")

        # 创建标题文字标签
        self.title_label = QLabel(self.parent_widget.windowTitle())
        # 标题文字向上偏移3px
        self.title_label.setStyleSheet(f"font-size: {self.config.FONT_SIZE}px; padding-bottom: 3px;")

        # 添加到布局
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()

    def _create_buttons(self):
        """创建控制按钮"""
        buttons_to_add = []

        # 隐藏到系统托盘按钮
        if self.show_systray:
            self.systray_button = self._create_circle_button(
                *self.config.COLORS["systray"], "systray", self.minimize_to_tray
            )
            buttons_to_add.append(self.systray_button)

        # 最小化按钮
        if self.show_minimize:
            self.minus_button = self._create_circle_button(
                *self.config.COLORS["minimize"], "minimize", self.minimize_with_animation
            )
            buttons_to_add.append(self.minus_button)

        # 关闭按钮 - 使用主窗口的关闭行为
        if self.show_close:
            self.close_button = self._create_circle_button(
                *self.config.COLORS["close"], "close", self._handle_close_button
            )
            buttons_to_add.append(self.close_button)

        # 按新顺序添加按钮到布局
        for button in buttons_to_add:
            self.layout.addWidget(button)

    def _handle_close_button(self):
        """处理关闭按钮点击事件"""
        # 触发主窗口的closeEvent，这样会根据配置决定是最小化到托盘还是直接关闭
        if self.parent_widget:
            self.parent_widget.close()

    def _create_circle_button(self, default_color, hover_color, icon_key, click_handler):
        """创建圆形按钮"""
        button = CircleButton(self)
        button.setFixedSize(self.config.BUTTON_SIZE, self.config.BUTTON_SIZE)
        button.setColors(default_color, hover_color)

        # 获取图标路径并设置图标
        icon_path = self._get_icon_path(icon_key)
        if icon_path:
            button.setIcon(icon_path)
        else:
            # 如果图标不存在，设置默认文本或样式
            logger.warning(f"使用默认样式替代缺失的图标: {icon_key}")

        button.setIconSize(self.config.ICON_SIZE)
        button.clicked.connect(click_handler)
        return button

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_pos = event.globalPosition().toPoint() - self.parent_widget.frameGeometry().topLeft()
            self._is_tracking = True
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self._is_tracking and event.buttons() == Qt.MouseButton.LeftButton:
            self.parent_widget.move(event.globalPosition().toPoint() - self._start_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self._is_tracking = False

    def minimize_to_tray(self):
        """最小化到系统托盘"""
        if self.minimize_animations is None:
            self.minimize_animations = QParallelAnimationGroup()

            # 透明度动画
            opacity_animation = QPropertyAnimation(self.parent_widget, b"windowOpacity")
            opacity_animation.setDuration(300)
            opacity_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
            opacity_animation.setStartValue(1.0)
            opacity_animation.setEndValue(0.0)

            # 缩放动画
            geometry_animation = QPropertyAnimation(self.parent_widget, b"geometry")
            geometry_animation.setDuration(300)
            geometry_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

            self.minimize_animations.addAnimation(opacity_animation)
            self.minimize_animations.addAnimation(geometry_animation)
            self.minimize_animations.finished.connect(self._on_tray_minimize_finished)

        # 保存原始几何信息到主窗口，供恢复使用
        current_geometry = self.parent_widget.geometry()
        if hasattr(self.parent_widget, "original_geometry"):
            self.parent_widget.original_geometry = QRect(current_geometry)

        final_geometry = QRect(current_geometry)

        # 获取系统托盘位置（屏幕右下角）
        screen = self.parent_widget.screen()
        screen_geometry = screen.geometry()
        tray_pos = QPoint(screen_geometry.right() - 20, screen_geometry.bottom() - 20)

        # 设置缩放终点
        final_geometry.setWidth(int(current_geometry.width() * 0.05))
        final_geometry.setHeight(int(current_geometry.height() * 0.05))
        final_geometry.moveCenter(tray_pos)

        self.minimize_animations.animationAt(1).setStartValue(current_geometry)
        self.minimize_animations.animationAt(1).setEndValue(final_geometry)

        # 设置主窗口的自定义最小化标志
        if hasattr(self.parent_widget, "is_custom_minimized"):
            self.parent_widget.is_custom_minimized = True

        self.minimize_animations.start()

    def minimize_with_animation(self):
        """最小化到任务栏"""
        if self.taskbar_animation is None:
            self.taskbar_animation = QPropertyAnimation(self.parent_widget, b"windowOpacity")
            self.taskbar_animation.setDuration(200)
            self.taskbar_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.taskbar_animation.finished.connect(self._on_taskbar_minimize_finished)

        self.taskbar_animation.setStartValue(1.0)
        self.taskbar_animation.setEndValue(0.0)
        self.taskbar_animation.start()

    def _on_tray_minimize_finished(self):
        """托盘最小化动画完成后的处理"""
        try:
            self.parent_widget.hide()  # 隐藏窗口

            # 重置动画组
            if self.minimize_animations:
                self.minimize_animations.stop()

            # 更新托盘菜单文本
            if hasattr(self.parent_widget, "update_tray_menu_text"):
                self.parent_widget.update_tray_menu_text()

            logger.debug("窗口已通过自定义标题栏最小化到托盘")

        except Exception as e:
            logger.error(f"托盘最小化完成处理错误: {str(e)}")

    def _on_taskbar_minimize_finished(self):
        """任务栏最小化动画完成后的处理"""
        self.parent_widget.showMinimized()
        self.parent_widget.setWindowOpacity(1.0)

    def safe_restore_window(self):
        """安全恢复窗口的方法"""
        try:
            # 创建恢复动画组
            restore_animations = QParallelAnimationGroup()

            # 获取系统托盘位置（屏幕右下角）
            screen = self.parent_widget.screen()
            screen_geometry = screen.geometry()
            tray_pos = QPoint(screen_geometry.right() - 20, screen_geometry.bottom() - 20)

            # 设置起始几何信息（小窗口在托盘位置）
            start_geometry = QRect(0, 0, 30, 30)  # 小窗口大小
            start_geometry.moveCenter(tray_pos)

            # 获取目标几何信息
            if (
                hasattr(self.parent_widget, "original_geometry")
                and self.parent_widget.original_geometry
                and self.parent_widget.original_geometry.isValid()
            ):
                final_geometry = QRect(self.parent_widget.original_geometry)
            else:
                # 如果没有保存的几何信息，使用默认位置
                final_geometry = QRect(self.parent_widget.geometry())
                center = screen_geometry.center()
                final_geometry.moveCenter(center)

            # 设置窗口初始状态
            self.parent_widget.setWindowOpacity(0.0)
            self.parent_widget.setGeometry(start_geometry)
            self.parent_widget.show()

            # 创建透明度动画
            opacity_animation = QPropertyAnimation(self.parent_widget, b"windowOpacity")
            opacity_animation.setDuration(300)
            opacity_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
            opacity_animation.setStartValue(0.0)
            opacity_animation.setEndValue(1.0)

            # 创建几何动画
            geometry_animation = QPropertyAnimation(self.parent_widget, b"geometry")
            geometry_animation.setDuration(300)
            geometry_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
            geometry_animation.setStartValue(start_geometry)
            geometry_animation.setEndValue(final_geometry)

            # 添加动画到组
            restore_animations.addAnimation(opacity_animation)
            restore_animations.addAnimation(geometry_animation)

            # 动画结束后的处理
            restore_animations.finished.connect(lambda: self._on_restore_animation_finished(restore_animations))

            # 启动动画
            restore_animations.start()

            logger.debug("窗口正在从托盘恢复，带动画效果")

        except Exception as e:
            logger.error(f"安全恢复窗口失败: {str(e)}")

    def _on_restore_animation_finished(self, animation_group):
        """恢复动画完成后的处理"""
        try:
            # 确保窗口完全显示
            self.parent_widget.showNormal()
            self.parent_widget.activateWindow()
            self.parent_widget.raise_()

            # 重置自定义最小化标志
            if hasattr(self.parent_widget, "is_custom_minimized"):
                self.parent_widget.is_custom_minimized = False

            # 清理动画资源
            animation_group.deleteLater()

            logger.debug("窗口从托盘恢复动画完成")

        except Exception as e:
            logger.error(f"恢复动画完成处理错误: {str(e)}")
