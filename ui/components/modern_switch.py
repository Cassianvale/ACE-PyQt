#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import QAbstractButton
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush


class ModernSwitch(QAbstractButton):

    stateChanged = pyqtSignal(int)

    def __init__(self, text: str = "", parent=None):
        super().__init__(parent)  # 先传入parent
        self.setText(text)  # 然后设置文本
        self.setCheckable(True)
        self.setFixedSize(50, 20)
        self._bg_color = QColor(200, 200, 200)
        self._circle_color = QColor(255, 255, 255)
        self._checked_bg_color = QColor(0, 120, 215)
        self._checked_circle_color = QColor(255, 255, 255)
        self._circle_position = 2

        # 初始化动画
        self._animation = QPropertyAnimation(self, b"circle_position")
        self._animation.setEasingCurve(QEasingCurve.Type.OutBounce)  # 弹性缓动曲线
        self._animation.setDuration(500)  # 动画持续时间

        self.toggled.connect(self._on_toggled)

        # 在初始化时更新圆圈位置
        self._update_circle_position()

    def sizeHint(self):
        return QSize(50, 20)

    def _on_toggled(self, checked):
        self._animate(checked)

    def _animate(self, checked):
        """检查开关状态"""
        self._animation.stop()
        if checked:
            self._animation.setEndValue(self.width() - self.height() + 2)
        else:
            self._animation.setEndValue(2)  # 设置动画结束值，用于匹配未选中状态
        self._animation.start()

    def resizeEvent(self, event):
        """动态计算圆圈位置"""
        self._circle_position = self.width() - self.height() + 2 if self.isChecked() else 2
        self.update()
        super().resizeEvent(event)

    def paintEvent(self, event):
        """
        重写paintEvent以自定义绘制控件。

        :param event: QPaintEvent, 绘制事件。
        """
        painter = QPainter(self)
        # 启用反锯齿
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 根据控件状态设置背景颜色
        if self.isChecked():
            painter.setBrush(QBrush(self._checked_bg_color))
        else:
            painter.setBrush(QBrush(self._bg_color))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height() / 2, self.height() / 2)

        circle_diameter = self.height() - 4
        circle_x = int(self._circle_position)
        circle_y = int((self.height() - circle_diameter) / 2)

        # 根据控件状态设置滑块圆圈的颜色
        painter.setBrush(QBrush(self._circle_color if not self.isChecked() else self._checked_circle_color))
        # 绘制滑块圆圈
        painter.drawEllipse(circle_x, circle_y, circle_diameter, circle_diameter)

    def get_circle_position(self):
        return self._circle_position

    def set_circle_position(self, position):
        self._circle_position = position
        self.update()

    def setChecked(self, checked):
        old_state = self.isChecked()
        super().setChecked(checked)
        self._update_circle_position()
        self.update()

        # 发出 stateChanged 信号以兼容 QCheckBox
        # QCheckBox 的 stateChanged 信号传递的是 Qt.CheckState 值
        if old_state != checked:
            state = Qt.CheckState.Checked.value if checked else Qt.CheckState.Unchecked.value
            self.stateChanged.emit(state)

    def setFixedSize(self, w, h):
        super().setFixedSize(w, h)
        self._update_circle_position()
        self.update()

    def _update_circle_position(self):
        self._circle_position = self.width() - self.height() + 2 if self.isChecked() else 2

    circle_position = pyqtProperty(int, get_circle_position, set_circle_position)

    def mousePressEvent(self, event):
        """重写鼠标按下事件以确保发出 stateChanged 信号"""
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            old_state = self.isChecked()
            super().mousePressEvent(event)
            # 检查状态是否真的改变了
            if old_state != self.isChecked():
                state = Qt.CheckState.Checked.value if self.isChecked() else Qt.CheckState.Unchecked.value
                self.stateChanged.emit(state)

    def keyPressEvent(self, event):
        """重写键盘按下事件以确保发出 stateChanged 信号"""
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter) and self.isEnabled():
            old_state = self.isChecked()
            super().keyPressEvent(event)
            # 检查状态是否真的改变了
            if old_state != self.isChecked():
                state = Qt.CheckState.Checked.value if self.isChecked() else Qt.CheckState.Unchecked.value
                self.stateChanged.emit(state)
        else:
            super().keyPressEvent(event)
