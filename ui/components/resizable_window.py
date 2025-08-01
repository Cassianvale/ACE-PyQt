#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
窗口边缘拖拽调整大小组件
"""

from enum import Enum
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QRect, QTimer

from utils import logger


class ResizeDirection(Enum):
    """调整大小方向枚举"""

    NONE = 0
    BOTTOM = 1
    LEFT = 2
    RIGHT = 3
    BOTTOM_LEFT = 4
    BOTTOM_RIGHT = 5


class ResizableWindow:
    """窗口边缘拖拽调整大小功能类"""

    def __init__(self, window, edge_width=12, min_width=700, min_height=800):
        self.window = window
        self.edge_width = edge_width
        self.min_width = min_width
        self.min_height = min_height

        self.is_resizing = False
        self.resize_direction = ResizeDirection.NONE
        self.resize_start_pos = QPoint()
        self.resize_start_geometry = QRect()

        self.install_event_filter()
        logger.debug(f"ResizableWindow初始化完成，边缘宽度: {edge_width}px，最小尺寸: {min_width}x{min_height}")

    def install_event_filter(self):
        if not hasattr(self.window, "_original_mousePressEvent"):
            self.window._original_mousePressEvent = self.window.mousePressEvent
            self.window.mousePressEvent = self._mouse_press_event

        if not hasattr(self.window, "_original_mouseMoveEvent"):
            self.window._original_mouseMoveEvent = self.window.mouseMoveEvent
            self.window.mouseMoveEvent = self._mouse_move_event

        if not hasattr(self.window, "_original_mouseReleaseEvent"):
            self.window._original_mouseReleaseEvent = self.window.mouseReleaseEvent
            self.window.mouseReleaseEvent = self._mouse_release_event

        if not hasattr(self.window, "_original_leaveEvent"):
            self.window._original_leaveEvent = self.window.leaveEvent
            self.window.leaveEvent = self._leave_event

    def get_resize_direction(self, pos):
        rect = self.window.rect()
        x, y = pos.x(), pos.y()

        # 边缘检测
        at_left = x <= self.edge_width
        at_right = x >= rect.width() - self.edge_width
        at_bottom = y >= rect.height() - self.edge_width

        # 确定调整方向
        if at_bottom and at_left:
            return ResizeDirection.BOTTOM_LEFT
        elif at_bottom and at_right:
            return ResizeDirection.BOTTOM_RIGHT
        elif at_bottom:
            return ResizeDirection.BOTTOM
        elif at_left:
            return ResizeDirection.LEFT
        elif at_right:
            return ResizeDirection.RIGHT
        else:
            return ResizeDirection.NONE

    def _mouse_press_event(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            direction = self.get_resize_direction(pos)

            if direction != ResizeDirection.NONE:
                self.is_resizing = True
                self.resize_direction = direction
                self.resize_start_pos = event.globalPosition().toPoint()
                self.resize_start_geometry = self.window.geometry()
                event.accept()
                return
        if hasattr(self.window, "_original_mousePressEvent"):
            self.window._original_mousePressEvent(event)

    def _mouse_move_event(self, event):
        if self.is_resizing:
            self._perform_resize(event.globalPosition().toPoint())
            event.accept()
            return
        if hasattr(self.window, "_original_mouseMoveEvent"):
            self.window._original_mouseMoveEvent(event)

    def _mouse_release_event(self, event):
        if self.is_resizing and event.button() == Qt.MouseButton.LeftButton:
            self.is_resizing = False
            self.resize_direction = ResizeDirection.NONE

            # 保存窗口尺寸到配置文件
            self._save_window_size()

            event.accept()
            return
        if hasattr(self.window, "_original_mouseReleaseEvent"):
            self.window._original_mouseReleaseEvent(event)

    def _leave_event(self, event):
        if hasattr(self.window, "_original_leaveEvent"):
            self.window._original_leaveEvent(event)

    def _perform_resize(self, global_pos):
        if self.resize_direction == ResizeDirection.NONE:
            return

        delta = global_pos - self.resize_start_pos
        dx, dy = delta.x(), delta.y()

        orig_rect = QRect(self.resize_start_geometry)
        new_rect = QRect(orig_rect)
        if self.resize_direction == ResizeDirection.BOTTOM:
            new_rect.setBottom(orig_rect.bottom() + dy)
        elif self.resize_direction == ResizeDirection.LEFT:
            new_rect.setLeft(orig_rect.left() + dx)
        elif self.resize_direction == ResizeDirection.RIGHT:
            new_rect.setRight(orig_rect.right() + dx)
        elif self.resize_direction == ResizeDirection.BOTTOM_LEFT:
            new_rect.setBottom(orig_rect.bottom() + dy)
            new_rect.setLeft(orig_rect.left() + dx)
        elif self.resize_direction == ResizeDirection.BOTTOM_RIGHT:
            new_rect.setBottom(orig_rect.bottom() + dy)
            new_rect.setRight(orig_rect.right() + dx)

        new_rect = self._apply_size_constraints(new_rect)
        self.window.setGeometry(new_rect)

    def _apply_size_constraints(self, rect):
        if rect.width() < self.min_width:
            if self.resize_direction in [ResizeDirection.LEFT, ResizeDirection.BOTTOM_LEFT]:
                rect.setLeft(rect.right() - self.min_width)
            else:
                rect.setWidth(self.min_width)

        if rect.height() < self.min_height:
            rect.setHeight(self.min_height)

        return rect

    def _save_window_size(self):
        """保存窗口尺寸到配置文件"""
        try:
            # 获取当前窗口尺寸
            current_geometry = self.window.geometry()
            width = current_geometry.width()
            height = current_geometry.height()

            # 通过主窗口的config_manager保存尺寸
            if hasattr(self.window, "config_manager") and self.window.config_manager:
                self.window.config_manager.save_window_size(width, height)
            else:
                logger.warning("无法访问config_manager，窗口尺寸未保存")

        except Exception as e:
            logger.error(f"保存窗口尺寸时发生错误: {str(e)}")
