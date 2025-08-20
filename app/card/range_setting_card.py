#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Range Setting Card - Slider-based numeric configuration card
Enhanced based on March7thAssistant design patterns
"""

from qfluentwidgets import SettingCard, FluentIconBase, Slider, InfoBar, InfoBarPosition
from typing import Union, Optional, Tuple
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QLabel, QToolButton, QHBoxLayout
from qfluentwidgets import FluentIcon as FIF
from utils.logger import logger


class RangeSettingCard(SettingCard):
    """
    Range Setting Card with slider and increment/decrement buttons
    参考 March7thAssistant 的 RangeSettingCard1 设计，支持多种交互方式
    """
    
    valueChanged = pyqtSignal(int)
    
    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title: str, 
                 content: Optional[str] = None, value_range: Tuple[int, int] = (0, 100),
                 configname: Optional[str] = None, business_handler: Optional[callable] = None,
                 suffix: str = "", show_buttons: bool = True, parent=None):
        """
        Initialize range setting card
        
        Args:
            icon: Card icon
            title (str): Card title
            content (str, optional): Card description
            value_range (tuple): (min_value, max_value) range
            configname (str, optional): Configuration key for auto-binding
            business_handler (callable, optional): Business logic handler function
            suffix (str): Value display suffix (e.g., "px", "%", "秒")
            show_buttons (bool): Whether to show increment/decrement buttons
            parent: Parent widget
        """
        super().__init__(icon, title, content, parent)
        
        self.configname = configname
        self.business_handler = business_handler
        self.value_range = value_range
        self.suffix = suffix
        self.show_buttons = show_buttons
        self._initializing = False
        
        # 创建控件
        self._setup_widgets()
        
        # 如果有配置名称，自动加载初始值
        if self.configname:
            self._load_from_config()
        
        # 连接信号
        self.slider.valueChanged.connect(self._on_value_changed)
        if self.show_buttons:
            self.minusButton.clicked.connect(self._decrease_value)
            self.plusButton.clicked.connect(self._increase_value)
    
    def _setup_widgets(self):
        """设置内部控件"""
        # 创建滑块
        self.slider = Slider(Qt.Horizontal, self)
        self.slider.setRange(self.value_range[0], self.value_range[1])
        
        # 创建数值显示标签
        self.valueLabel = QLabel(self)
        self.valueLabel.setMinimumWidth(50)
        self.valueLabel.setAlignment(Qt.AlignCenter)
        
        # 创建增减按钮（如果需要）
        if self.show_buttons:
            self.minusButton = QToolButton(self)
            self.plusButton = QToolButton(self)
            
            self.minusButton.setIcon(FIF.REMOVE.icon())
            self.plusButton.setIcon(FIF.ADD.icon())
            
            self.minusButton.setFixedSize(24, 24)
            self.plusButton.setFixedSize(24, 24)
        
        # 设置布局
        self._setup_layout()
        
        # 初始化显示
        self._update_value_display(self.slider.value())
    
    def _setup_layout(self):
        """设置控件布局"""
        # 创建控件容器
        widget_layout = QHBoxLayout()
        
        if self.show_buttons:
            widget_layout.addWidget(self.minusButton)
        
        widget_layout.addWidget(self.slider)
        widget_layout.addWidget(self.valueLabel)
        
        if self.show_buttons:
            widget_layout.addWidget(self.plusButton)
        
        widget_layout.setSpacing(8)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加到卡片布局
        self.hBoxLayout.addLayout(widget_layout)
        self.hBoxLayout.addSpacing(16)
    
    def set_business_handler(self, handler):
        """
        Set the business logic handler
        
        Args:
            handler (callable): Function to handle business logic
        """
        self.business_handler = handler
    
    def set_config_name(self, configname: str):
        """
        设置配置名称并自动加载值
        
        Args:
            configname (str): 配置键名
        """
        self.configname = configname
        self._load_from_config()
    
    def refresh_from_config(self):
        """
        从配置系统刷新当前值
        """
        if self.configname:
            self._load_from_config()
    
    def set_range(self, min_value: int, max_value: int):
        """
        设置数值范围
        
        Args:
            min_value (int): 最小值
            max_value (int): 最大值
        """
        self.value_range = (min_value, max_value)
        self.slider.setRange(min_value, max_value)
        
        # 确保当前值在新范围内
        current_value = self.slider.value()
        if current_value < min_value:
            self.slider.setValue(min_value)
        elif current_value > max_value:
            self.slider.setValue(max_value)
    
    def load_value(self, value: int):
        """
        Load value from configuration (without triggering business logic)
        
        Args:
            value (int): Configuration value
        """
        self._initializing = True
        try:
            # 确保值在范围内
            clamped_value = max(self.value_range[0], min(self.value_range[1], value))
            self.slider.setValue(clamped_value)
            self._update_value_display(clamped_value)
            logger.debug(f"Loaded value for {self.titleLabel.text()}: {clamped_value}")
        finally:
            self._initializing = False
    
    def _load_from_config(self):
        """
        从配置系统自动加载初始值
        """
        if not self.configname:
            return
            
        try:
            from module.config import cfg
            initial_value = getattr(cfg, self.configname, self.value_range[0])
            self.load_value(int(initial_value))
            logger.debug(f"Auto-loaded config {self.configname}: {initial_value}")
        except Exception as e:
            logger.error(f"Failed to load config {self.configname}: {str(e)}")
    
    def _save_to_config(self, value: int) -> bool:
        """
        将值保存到配置系统
        
        Args:
            value (int): 要保存的值
            
        Returns:
            bool: 保存是否成功
        """
        if not self.configname:
            return True  # 没有配置绑定，视为成功
            
        try:
            from module.config import cfg
            setattr(cfg, self.configname, value)
            success = cfg.save_config()
            
            if success:
                logger.debug(f"Saved config {self.configname}: {value}")
            else:
                logger.error(f"Failed to save config {self.configname}: {value}")
                
            return success
        except Exception as e:
            logger.error(f"Exception saving config {self.configname}: {str(e)}")
            return False
    
    def get_value(self) -> int:
        """
        Get current value
        
        Returns:
            int: Current slider value
        """
        return self.slider.value()
    
    def _update_value_display(self, value: int):
        """
        更新数值显示
        
        Args:
            value (int): 当前值
        """
        display_text = f"{value}{self.suffix}"
        self.valueLabel.setText(display_text)
    
    def _on_value_changed(self, value: int):
        """
        Handle slider value change
        
        Args:
            value (int): New slider value
        """
        # Skip if we're initializing
        if self._initializing:
            return
        
        # 更新显示
        self._update_value_display(value)
        
        try:
            # 优先使用业务逻辑处理器
            if self.business_handler:
                success = self.business_handler(value)
                if not success:
                    # 回滚到之前的值（这里简化处理，记录错误但不回滚）
                    self._show_error_feedback("业务逻辑处理失败")
                    return
            
            # 自动保存到配置系统
            config_success = self._save_to_config(value)
            if not config_success:
                self._show_error_feedback("配置保存失败")
                return
            
            # 发送成功信号
            self.valueChanged.emit(value)
            logger.debug(f"Range setting changed for {self.titleLabel.text()}: {value}")
            
        except Exception as e:
            logger.error(f"Error handling range change for {self.titleLabel.text()}: {str(e)}")
            self._show_error_feedback(f"操作失败: {str(e)}")
    
    def _increase_value(self):
        """增加数值"""
        current = self.slider.value()
        new_value = min(current + 1, self.value_range[1])
        self.slider.setValue(new_value)
    
    def _decrease_value(self):
        """减少数值"""
        current = self.slider.value()
        new_value = max(current - 1, self.value_range[0])
        self.slider.setValue(new_value)
    
    def _show_error_feedback(self, message: str):
        """
        显示错误反馈
        
        Args:
            message (str): 错误信息
        """
        try:
            InfoBar.error(
                title="设置失败",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent() or self.window()
            )
        except Exception as e:
            logger.error(f"Failed to show error feedback: {str(e)}")