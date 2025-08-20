#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Switch Setting Card - Boolean configuration card that automatically binds to business logic
Enhanced based on March7thAssistant design patterns
"""

from qfluentwidgets import SettingCard, FluentIconBase, SwitchButton, InfoBar, InfoBarPosition
from typing import Union, Optional
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, Qt
from app.tools import logger


class SwitchSettingCard(SettingCard):
    """
    Enhanced Switch Setting Card with automatic configuration binding and enhanced UX
    参考 March7thAssistant 的设计模式，支持自动配置绑定和智能用户反馈
    """

    valueChanged = pyqtSignal(bool)
    
    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title: str, content: Optional[str] = None, 
                 configname: Optional[str] = None, business_handler: Optional[callable] = None, 
                 show_indicator: bool = True, parent=None):
        """
        Initialize switch setting card
        
        Args:
            icon: Card icon
            title (str): Card title
            content (str, optional): Card description
            configname (str, optional): Configuration key for auto-binding
            business_handler (callable, optional): Business logic handler function
            show_indicator (bool): Whether to show switch text indicator
            parent: Parent widget
        """
        super().__init__(icon, title, content, parent)
        
        self.configname = configname
        self.business_handler = business_handler
        self.show_indicator = show_indicator
        self._initializing = False


        self.switchButton = SwitchButton(self)
        self.hBoxLayout.addWidget(self.switchButton, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        if self.show_indicator:
            self.switchButton.setText(self.tr("off"))
            
        # 如果有配置名称，自动加载初始值
        if self.configname:
            self._load_from_config()
        
        # Connect internal signal
        self.switchButton.checkedChanged.connect(self._on_checked_changed)
    
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
    
    def load_value(self, value: bool):
        """
        Load value from configuration (without triggering business logic)
        
        Args:
            value (bool): Configuration value
        """
        self._initializing = True
        try:
            self.switchButton.setChecked(value)
            # 更新开关状态文字显示
            if self.show_indicator:
                self.switchButton.setText(self.tr("on") if value else self.tr("off"))
            logger.debug(f"Loaded value for {self.titleLabel.text()}: {value}")
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
            initial_value = getattr(cfg, self.configname, False)
            self.load_value(initial_value)
            logger.debug(f"Auto-loaded config {self.configname}: {initial_value}")
        except Exception as e:
            logger.error(f"Failed to load config {self.configname}: {str(e)}")
    
    def _save_to_config(self, value: bool) -> bool:
        """
        将值保存到配置系统
        
        Args:
            value (bool): 要保存的值
            
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
    
    def get_value(self) -> bool:
        """
        Get current value
        
        Returns:
            bool: Current switch state
        """
        return self.switchButton.isChecked()
    
    def _on_checked_changed(self, checked: bool):
        """
        Handle check state change with enhanced error handling and user feedback
        
        Args:
            checked (bool): New check state
        """
        # Skip if we're initializing
        if self._initializing:
            return
        
        # 更新开关状态文字显示
        if self.show_indicator:
            self.switchButton.setText(self.tr('开') if checked else self.tr('关'))
        
        try:
            # 优先使用业务逻辑处理器
            if self.business_handler:
                success = self.business_handler(checked)
                if not success:
                    self._revert_state(not checked)
                    self._show_error_feedback("业务逻辑处理失败")
                    return
            
            # 自动保存到配置系统
            config_success = self._save_to_config(checked)
            if not config_success:
                self._revert_state(not checked)
                self._show_error_feedback("配置保存失败")
                return
            
            # 发送成功信号
            self.valueChanged.emit(checked)
            logger.debug(f"Setting changed for {self.titleLabel.text()}: {checked}")
            
        except Exception as e:
            logger.error(f"Error handling setting change for {self.titleLabel.text()}: {str(e)}")
            self._revert_state(not checked)
            self._show_error_feedback(f"操作失败: {str(e)}")
    
    def _revert_state(self, old_value: bool):
        """
        回滚到之前的状态
        
        Args:
            old_value (bool): 要回滚到的值
        """
        self._initializing = True
        try:
            self.switchButton.setChecked(old_value)
            if self.show_indicator:
                self.switchButton.setText(self.tr("on") if old_value else self.tr("off"))
        finally:
            self._initializing = False
    
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