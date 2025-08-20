#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time Setting Card - Time picker configuration card
Enhanced based on March7thAssistant design patterns
"""

from qfluentwidgets import SettingCard, FluentIconBase, TimePicker, InfoBar, InfoBarPosition
from typing import Union, Optional
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, Qt, QTime
from utils.logger import logger


class TimeSettingCard(SettingCard):
    """
    Time Setting Card with time picker
    参考 March7thAssistant 的 TimePickerSettingCard1 设计
    """
    
    valueChanged = pyqtSignal(str)  # 发送 "HH:mm" 格式的时间字符串
    timeChanged = pyqtSignal(QTime)  # 发送 QTime 对象
    
    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title: str, 
                 content: Optional[str] = None, configname: Optional[str] = None,
                 business_handler: Optional[callable] = None, time_format: str = "HH:mm",
                 parent=None):
        """
        Initialize time setting card
        
        Args:
            icon: Card icon
            title (str): Card title
            content (str, optional): Card description
            configname (str, optional): Configuration key for auto-binding
            business_handler (callable, optional): Business logic handler function
            time_format (str): Time format string (default: "HH:mm")
            parent: Parent widget
        """
        super().__init__(icon, title, content, parent)
        
        self.configname = configname
        self.business_handler = business_handler
        self.time_format = time_format
        self._initializing = False
        
        # 创建时间选择器
        self.timePicker = TimePicker(self)
        
        # 设置布局
        self.hBoxLayout.addWidget(self.timePicker, 0)
        self.hBoxLayout.addSpacing(16)
        
        # 如果有配置名称，自动加载初始值
        if self.configname:
            self._load_from_config()
        
        # 连接信号
        self.timePicker.timeChanged.connect(self._on_time_changed)
    
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
    
    def set_time_format(self, format_string: str):
        """
        设置时间格式
        
        Args:
            format_string (str): 时间格式字符串
        """
        self.time_format = format_string
    
    def load_time_string(self, time_string: str):
        """
        Load time from string (without triggering business logic)
        
        Args:
            time_string (str): Time string in format "HH:mm" or similar
        """
        self._initializing = True
        try:
            time = QTime.fromString(time_string, self.time_format)
            if time.isValid():
                self.timePicker.setTime(time)
                logger.debug(f"Loaded time for {self.titleLabel.text()}: {time_string}")
            else:
                logger.warning(f"Invalid time string for {self.titleLabel.text()}: {time_string}")
        finally:
            self._initializing = False
    
    def load_time(self, time: QTime):
        """
        Load QTime object (without triggering business logic)
        
        Args:
            time (QTime): Time object
        """
        self._initializing = True
        try:
            if time.isValid():
                self.timePicker.setTime(time)
                logger.debug(f"Loaded time for {self.titleLabel.text()}: {time.toString(self.time_format)}")
            else:
                logger.warning(f"Invalid QTime for {self.titleLabel.text()}")
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
            initial_value = getattr(cfg, self.configname, "00:00")
            
            if isinstance(initial_value, str):
                self.load_time_string(initial_value)
            elif isinstance(initial_value, QTime):
                self.load_time(initial_value)
            else:
                # 尝试转换为字符串
                self.load_time_string(str(initial_value))
                
            logger.debug(f"Auto-loaded config {self.configname}: {initial_value}")
        except Exception as e:
            logger.error(f"Failed to load config {self.configname}: {str(e)}")
    
    def _save_to_config(self, time_string: str) -> bool:
        """
        将时间字符串保存到配置系统
        
        Args:
            time_string (str): 要保存的时间字符串
            
        Returns:
            bool: 保存是否成功
        """
        if not self.configname:
            return True  # 没有配置绑定，视为成功
            
        try:
            from module.config import cfg
            setattr(cfg, self.configname, time_string)
            success = cfg.save_config()
            
            if success:
                logger.debug(f"Saved config {self.configname}: {time_string}")
            else:
                logger.error(f"Failed to save config {self.configname}: {time_string}")
                
            return success
        except Exception as e:
            logger.error(f"Exception saving config {self.configname}: {str(e)}")
            return False
    
    def get_time(self) -> QTime:
        """
        Get current time as QTime object
        
        Returns:
            QTime: Current selected time
        """
        return self.timePicker.time
    
    def get_time_string(self) -> str:
        """
        Get current time as formatted string
        
        Returns:
            str: Current time in specified format
        """
        return self.timePicker.time.toString(self.time_format)
    
    def _on_time_changed(self, time: QTime):
        """
        Handle time change
        
        Args:
            time (QTime): New selected time
        """
        # Skip if we're initializing
        if self._initializing:
            return
        
        try:
            time_string = time.toString(self.time_format)
            
            # 优先使用业务逻辑处理器
            if self.business_handler:
                success = self.business_handler(time_string)
                if not success:
                    self._show_error_feedback("业务逻辑处理失败")
                    return
            
            # 自动保存到配置系统
            config_success = self._save_to_config(time_string)
            if not config_success:
                self._show_error_feedback("配置保存失败")
                return
            
            # 发送成功信号
            self.valueChanged.emit(time_string)
            self.timeChanged.emit(time)
            logger.debug(f"Time setting changed for {self.titleLabel.text()}: {time_string}")
            
        except Exception as e:
            logger.error(f"Error handling time change for {self.titleLabel.text()}: {str(e)}")
            self._show_error_feedback(f"操作失败: {str(e)}")
    
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