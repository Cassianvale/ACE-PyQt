#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""自定义选项卡栏组件，支持左侧选项卡的水平文本显示"""

from PyQt6.QtWidgets import QTabBar, QTabWidget, QStylePainter, QStyle, QStyleOptionTab
from PyQt6.QtCore import QSize, QRect, QPoint, Qt
from PyQt6.QtGui import QPaintEvent, QFontMetrics


class HorizontalTextTabBar(QTabBar):
    """自定义选项卡栏，确保左侧选项卡文本水平显示"""

    def tabSizeHint(self, index: int) -> QSize:
        """重写选项卡大小提示，为左侧选项卡优化尺寸"""
        size = super().tabSizeHint(index)

        # 如果是左侧或右侧选项卡，需要调整尺寸
        if self.parent() and hasattr(self.parent(), "tabPosition"):
            position = self.parent().tabPosition()
            if position in (QTabWidget.TabPosition.West, QTabWidget.TabPosition.East):
                # 获取文本内容来计算合适的宽度
                text = self.tabText(index)
                font_metrics = QFontMetrics(self.font())
                text_width = font_metrics.horizontalAdvance(text)

                # 为左侧选项卡设置合适的尺寸
                width = max(text_width + 24, 100)  # 文本宽度 + 内边距，最小100px
                height = max(size.height(), 36)  # 最小高度36px
                return QSize(width, height)

        return size

    def paintEvent(self, event: QPaintEvent):
        """重写绘制事件，确保文本水平显示"""
        painter = QStylePainter(self)

        # 获取选项卡位置
        tab_position = QTabWidget.TabPosition.North
        if self.parent() and hasattr(self.parent(), "tabPosition"):
            tab_position = self.parent().tabPosition()

        # 绘制每个选项卡
        for i in range(self.count()):
            opt = QStyleOptionTab()
            self.initStyleOption(opt, i)

            # 绘制选项卡形状
            painter.drawControl(QStyle.ControlElement.CE_TabBarTabShape, opt)

            # 如果是左侧或右侧选项卡，需要特殊处理文本
            if tab_position in (QTabWidget.TabPosition.West, QTabWidget.TabPosition.East):
                self._draw_horizontal_text(painter, opt, i, tab_position)
            else:
                # 对于顶部和底部选项卡，正常绘制
                painter.drawControl(QStyle.ControlElement.CE_TabBarTabLabel, opt)

    def _draw_horizontal_text(self, painter, opt, index: int, tab_position):
        """绘制水平文本（用于左侧和右侧选项卡）"""
        painter.save()

        # 获取选项卡矩形
        tab_rect = self.tabRect(index)

        # 创建文本绘制区域
        text_rect = QRect(tab_rect)

        # 根据选项卡位置调整文本区域
        if tab_position == QTabWidget.TabPosition.West:
            # 左侧选项卡：文本区域稍微向右偏移，增加内边距
            text_rect.adjust(12, 6, -12, -6)
        elif tab_position == QTabWidget.TabPosition.East:
            # 右侧选项卡：文本区域稍微向左偏移
            text_rect.adjust(12, 6, -12, -6)

        # 设置文本对齐方式
        text_flags = Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextSingleLine

        # 获取文本内容
        text = self.tabText(index)

        # 设置文本颜色
        if opt.state & QStyle.StateFlag.State_Selected:
            # 选中状态的颜色
            painter.setPen(opt.palette.color(opt.palette.ColorRole.Highlight))
        else:
            # 未选中状态的颜色
            painter.setPen(opt.palette.color(opt.palette.ColorRole.WindowText))

        # 绘制水平文本
        painter.drawText(text_rect, text_flags, text)

        painter.restore()


class CustomTabWidget(QTabWidget):
    """使用自定义选项卡栏的选项卡组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置自定义选项卡栏
        self.setTabBar(HorizontalTextTabBar())

        # 确保能正确应用 styles.py 中的样式
        self._apply_initial_styles()

    def _apply_initial_styles(self):
        """应用初始样式属性"""
        # 这个方法确保 CustomTabWidget 能正确应用 styles.py 中的样式
        # 如果需要特定的样式属性，可以在这里设置
        pass

    def setTabPosition(self, position):
        """重写设置选项卡位置方法"""
        super().setTabPosition(position)

        # 设置选项卡位置属性，让 styles.py 中的样式能正确应用
        position_names = {
            self.TabPosition.North: "North",
            self.TabPosition.South: "South",
            self.TabPosition.West: "West",
            self.TabPosition.East: "East",
        }
        if position in position_names:
            self.setProperty("tabPosition", position_names[position])
            # 刷新样式
            self.style().unpolish(self)
            self.style().polish(self)

        # 刷新选项卡栏以应用新的绘制逻辑
        if self.tabBar():
            self.tabBar().update()
            # 重新计算选项卡大小
            for i in range(self.count()):
                self.tabBar().setTabData(i, None)  # 触发重新计算
