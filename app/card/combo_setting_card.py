#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qfluentwidgets import SettingCard, FluentIconBase, ComboBox, InfoBar, InfoBarPosition
from typing import Union, Optional, Dict, List
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, Qt
from app.tools import logger


class ComboBoxSettingCard(SettingCard):

    # 设置值变化信号
    valueChanged = pyqtSignal(str)
    
    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title: str, content: Optional[str] = None, 
                 texts: Optional[Union[List[str], Dict[str, str]]] = None, configname: Optional[str] = None,
                 business_handler: Optional[callable] = None, parent=None):
        """
        Initialize combo box setting card
        
        Args:
            icon: Card icon
            title (str): Card title
            content (str, optional): Card description
            texts (list or dict, optional): Options as list of strings or dict mapping values to display text
            configname (str, optional): Configuration key for auto-binding
            business_handler (callable, optional): Business logic handler function
            parent: Parent widget
        """
        super().__init__(icon, title, content, parent)
        
        self.configname = configname
        self.business_handler = business_handler
        self._initializing = False
        self._processing_change = False  # Recursion protection flag
        self._option_mapping = {}  # Maps display text to actual values
        self._reverse_mapping = {}  # Maps values to display text
        
        self.comboBox = ComboBox(self)
        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        
        # 设置选项
        if texts:
            self.set_options(texts)
            
        # 如果有配置名称，自动加载初始值
        if self.configname:
            self._load_from_config()
        
        # Connect internal signal - 在选项设置完成后连接
        self.comboBox.currentTextChanged.connect(self._on_text_changed)
    
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
    
    def set_options(self, options: Union[List[str], Dict[str, str]]):
        """
        Set available options with enhanced key-value mapping support
        
        Args:
            options (list or dict): List of option strings, or dict mapping values to display text
        """
        # 临时断开信号连接，避免在设置选项时触发
        try:
            self.comboBox.currentTextChanged.disconnect(self._on_text_changed)
        except:
            pass  # 如果没有连接则忽略错误
            
        self.comboBox.clear()
        self._option_mapping.clear()
        self._reverse_mapping.clear()
        
        if isinstance(options, dict):
            # Key-value mapping: {value: display_text}
            self._reverse_mapping = options.copy()
            self._option_mapping = {v: k for k, v in options.items()}
            
            for value, display_text in options.items():
                self.comboBox.addItem(display_text)
                # Store the actual value as user data
                index = self.comboBox.count() - 1
                self.comboBox.setItemData(index, value)
                
        elif isinstance(options, list):
            # Simple list: display text equals value
            for option in options:
                self.comboBox.addItem(option)
                index = self.comboBox.count() - 1
                self.comboBox.setItemData(index, option)
        else:
            logger.warning(f"Invalid options type for {self.titleLabel.text()}: {type(options)}")
        
        # 重新连接信号
        self.comboBox.currentTextChanged.connect(self._on_text_changed)
    
    def add_option(self, value: str, display_text: Optional[str] = None):
        """
        添加单个选项
        
        Args:
            value (str): 选项的实际值
            display_text (str, optional): 显示文本，如果不提供则使用value
        """
        display_text = display_text or value
        self.comboBox.addItem(display_text)
        
        index = self.comboBox.count() - 1
        self.comboBox.setItemData(index, value)
        
        # 更新映射
        self._option_mapping[display_text] = value
        self._reverse_mapping[value] = display_text
    
    def remove_option(self, value: str):
        """
        移除选项
        
        Args:
            value (str): 要移除的选项值
        """
        for i in range(self.comboBox.count()):
            if self.comboBox.itemData(i) == value:
                display_text = self.comboBox.itemText(i)
                self.comboBox.removeItem(i)
                
                # 更新映射
                self._option_mapping.pop(display_text, None)
                self._reverse_mapping.pop(value, None)
                break
    
    def load_value(self, value: str):
        """
        Load value from configuration (without triggering business logic)
        
        Args:
            value (str): Configuration value
        """
        self._initializing = True
        try:
            # 查找对应的显示文本
            display_text = self._reverse_mapping.get(value, value)
            
            # 设置组合框当前项
            index = self.comboBox.findText(display_text)
            if index >= 0:
                self.comboBox.setCurrentIndex(index)
                logger.debug(f"Loaded value for {self.titleLabel.text()}: {value} -> {display_text}")
            else:
                # 如果找不到匹配项，尝试直接设置文本
                self.comboBox.setCurrentText(value)
                logger.warning(f"Value not found in options for {self.titleLabel.text()}: {value}")
                
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
            initial_value = getattr(cfg, self.configname, '')
            if initial_value:
                self.load_value(str(initial_value))
                logger.debug(f"Auto-loaded config {self.configname}: {initial_value}")
        except Exception as e:
            logger.error(f"Failed to load config {self.configname}: {str(e)}")
    
    def _save_to_config(self, value: str) -> bool:
        """
        将值保存到配置系统
        
        Args:
            value (str): 要保存的值
            
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
    
    def get_value(self):
        """
        Get current value (actual value, not display text)
        
        Returns:
            Current selected value
        """
        current_data = self.comboBox.currentData()
        return current_data if current_data is not None else self.comboBox.currentText()
    
    def get_display_text(self) -> str:
        """
        Get current display text
        
        Returns:
            str: Current display text
        """
        return self.comboBox.currentText()
    
    def _on_text_changed(self, text: str):
        """
        Handle text change with enhanced error handling
        
        Args:
            text (str): New selected text
        """
        # Skip if we're initializing
        if self._initializing:
            return
            
        # Recursion protection
        if self._processing_change:
            logger.debug(f"Change already in progress for {self.titleLabel.text()}, ignoring")
            return
        
        try:
            self._processing_change = True
            
            # Get the actual value (might be different from display text)
            current_value = self.get_value()
            
            # 优先使用业务逻辑处理器
            if self.business_handler:
                success = self.business_handler(current_value)
                if not success:
                    # Note: 对于ComboBox，回滚比较复杂，这里记录错误但不回滚
                    self._show_error_feedback("业务逻辑处理失败")
                    return
            
            # 自动保存到配置系统
            config_success = self._save_to_config(current_value)
            if not config_success:
                self._show_error_feedback("配置保存失败")
                return
            
            # 发送成功信号
            self.valueChanged.emit(current_value)
            logger.debug(f"Setting changed for {self.titleLabel.text()}: {current_value}")
            
        except Exception as e:
            logger.error(f"Error handling setting change for {self.titleLabel.text()}: {str(e)}")
            self._show_error_feedback(f"操作失败: {str(e)}")
        finally:
            # Always clear the processing flag
            self._processing_change = False
    
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
    
    def get_option_count(self) -> int:
        """
        获取选项数量
        
        Returns:
            int: 选项数量
        """
        return self.comboBox.count()
    
    def get_all_options(self) -> Dict[str, str]:
        """
        获取所有选项的映射关系
        
        Returns:
            dict: {value: display_text} 映射
        """
        return self._reverse_mapping.copy()
    
    def find_option_by_value(self, value: str) -> Optional[str]:
        """
        根据值查找显示文本
        
        Args:
            value (str): 要查找的值
            
        Returns:
            str or None: 对应的显示文本，如果未找到返回None
        """
        return self._reverse_mapping.get(value)
    
    def find_option_by_display_text(self, display_text: str) -> Optional[str]:
        """
        根据显示文本查找值
        
        Args:
            display_text (str): 要查找的显示文本
            
        Returns:
            str or None: 对应的值，如果未找到返回None
        """
        return self._option_mapping.get(display_text)