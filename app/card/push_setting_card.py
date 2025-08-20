#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Push Setting Card - Action button configuration card with business logic integration
Enhanced based on March7thAssistant design patterns with dialog support
"""

from qfluentwidgets import SettingCard, FluentIconBase, InfoBar, InfoBarPosition, PushButton
from typing import Union, Optional, Dict, Any
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, Qt
from app.tools import logger
from .messagebox_custom import MessageBoxEdit, MessageBoxEditMultiple, MessageBoxDate, MessageBoxCombo, MessageBoxKeyBind, MessageBoxConfig


class PushSettingCard(SettingCard):
    """
    Enhanced Push Setting Card with business logic integration and dialog support
    参考 March7thAssistant 的设计模式，支持多种对话框类型和智能配置绑定
    """
    
    # 按钮点击信号
    actionRequested = pyqtSignal()
    valueChanged = pyqtSignal(object)  # 当配置值变化时发送
    
    def __init__(self, text: str, icon: Union[str, QIcon, FluentIconBase], title: str, 
                 content: Optional[str] = None, configname: Optional[str] = None,
                 business_handler: Optional[callable] = None, dialog_type: str = "none",
                 dialog_config: Optional[Dict] = None, parent=None):
        """
        Initialize push setting card
        
        Args:
            text (str): Button text
            icon: Card icon
            title (str): Card title
            content (str, optional): Card description
            configname (str, optional): Configuration key for auto-binding
            business_handler (callable, optional): Business logic handler function
            dialog_type (str): Dialog type ('none', 'text', 'multitext', 'date', 'combo', 'keybind', 'config')
            dialog_config (dict, optional): Dialog configuration
            parent: Parent widget
        """
        super().__init__(icon, title, content, parent)
        
        self.configname = configname
        self.business_handler = business_handler
        self.dialog_type = dialog_type
        self.dialog_config = dialog_config or {}
        self.original_button_text = text
        
        self.button = PushButton(text, self)
        self.hBoxLayout.addWidget(self.button, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        
        # 如果有配置名称，自动加载并显示当前值
        if self.configname:
            self._load_from_config()
        
        # Connect internal signal
        self.button.clicked.connect(self._on_clicked)
    
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
    
    def set_dialog_type(self, dialog_type: str, dialog_config: Optional[Dict] = None):
        """
        设置对话框类型和配置
        
        Args:
            dialog_type (str): 对话框类型
            dialog_config (dict, optional): 对话框配置
        """
        self.dialog_type = dialog_type
        self.dialog_config = dialog_config or {}
    
    def _load_from_config(self):
        """
        从配置系统自动加载初始值并更新显示
        """
        if not self.configname:
            return
            
        try:
            from module.config import cfg
            current_value = getattr(cfg, self.configname, None)
            
            if current_value is not None:
                # 更新内容显示
                self._update_content_display(current_value)
                logger.debug(f"Auto-loaded config {self.configname}: {current_value}")
        except Exception as e:
            logger.error(f"Failed to load config {self.configname}: {str(e)}")
    
    def _save_to_config(self, value: Any) -> bool:
        """
        将值保存到配置系统
        
        Args:
            value: 要保存的值
            
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
                # 更新显示
                self._update_content_display(value)
            else:
                logger.error(f"Failed to save config {self.configname}: {value}")
                
            return success
        except Exception as e:
            logger.error(f"Exception saving config {self.configname}: {str(e)}")
            return False
    
    def _update_content_display(self, value: Any):
        """
        根据值更新内容显示
        
        Args:
            value: 当前配置值
        """
        if value is None:
            return
            
        # 根据值类型和对话框类型更新显示
        if isinstance(value, str):
            if len(value) > 30:
                display_text = value[:30] + "..."
            else:
                display_text = value or "未设置"
        elif isinstance(value, (list, tuple)):
            display_text = f"{len(value)} 项配置"
        elif isinstance(value, dict):
            display_text = f"{len(value)} 项设置"
        else:
            display_text = str(value)
        
        # 更新内容标签
        self.contentLabel.setText(display_text)
    
    def _on_clicked(self):
        """
        Handle button click with dialog support
        """
        try:
            # 如果有对话框类型，显示对应对话框
            if self.dialog_type != "none":
                result = self._show_dialog()
                if result is not None:
                    # 保存结果
                    config_success = self._save_to_config(result)
                    if config_success:
                        # 调用业务逻辑处理器
                        if self.business_handler:
                            self.business_handler(result)
                        
                        # 发送值变化信号
                        self.valueChanged.emit(result)
                        
                        # 显示成功反馈
                        self._show_success_feedback("设置已保存")
                    else:
                        self._show_error_feedback("保存配置失败")
                return
            
            # 没有对话框，直接调用业务逻辑
            if self.business_handler:
                self.business_handler()
            
            # 发送动作请求信号
            self.actionRequested.emit()
            
        except Exception as e:
            logger.error(f"Error handling button click for {self.titleLabel.text()}: {str(e)}")
            self._show_error_feedback(f"操作失败: {str(e)}")
    
    def _show_dialog(self) -> Optional[Any]:
        """
        显示相应类型的对话框
        
        Returns:
            对话框返回的结果，如果取消则返回None
        """
        current_value = ""
        if self.configname:
            try:
                from module.config import cfg
                current_value = getattr(cfg, self.configname, "")
            except:
                pass
        
        dialog = None
        
        try:
            if self.dialog_type == "text":
                # 单行文本输入对话框
                dialog = MessageBoxEdit(
                    title=self.dialog_config.get('title', f"编辑 {self.titleLabel.text()}"),
                    content=str(current_value),
                    placeholder=self.dialog_config.get('placeholder', ''),
                    parent=self.window()
                )
                
                if dialog.exec():
                    return dialog.getText()
                    
            elif self.dialog_type == "multitext":
                # 多行文本输入对话框
                dialog = MessageBoxEditMultiple(
                    title=self.dialog_config.get('title', f"编辑 {self.titleLabel.text()}"),
                    content=str(current_value) if isinstance(current_value, str) else '\n'.join(current_value),
                    placeholder=self.dialog_config.get('placeholder', ''),
                    parent=self.window()
                )
                
                if dialog.exec():
                    text = dialog.getText()
                    # 根据配置决定返回字符串还是列表
                    if self.dialog_config.get('return_lines', False):
                        return dialog.getLines()
                    return text
                    
            elif self.dialog_type == "date":
                # 日期时间选择对话框
                import datetime
                current_date = current_value if isinstance(current_value, datetime.datetime) else datetime.datetime.now()
                dialog = MessageBoxDate(
                    title=self.dialog_config.get('title', f"选择 {self.titleLabel.text()}"),
                    content=current_date,
                    parent=self.window()
                )
                
                if dialog.exec():
                    return dialog.getDateTime()
                    
            elif self.dialog_type == "combo":
                # 下拉选择对话框
                options = self.dialog_config.get('options', [])
                dialog = MessageBoxCombo(
                    title=self.dialog_config.get('title', f"选择 {self.titleLabel.text()}"),
                    options=options,
                    current=str(current_value),
                    description=self.dialog_config.get('description', ''),
                    parent=self.window()
                )
                
                if dialog.exec():
                    return dialog.getSelectedText()
                    
            elif self.dialog_type == "keybind":
                # 快捷键绑定对话框
                dialog = MessageBoxKeyBind(
                    title=self.dialog_config.get('title', f"设置 {self.titleLabel.text()} 快捷键"),
                    current_key=str(current_value),
                    parent=self.window()
                )
                
                if dialog.exec():
                    return dialog.getKey()
                    
            elif self.dialog_type == "config":
                # 通用配置对话框
                config_items = self.dialog_config.get('items', {})
                dialog = MessageBoxConfig(
                    title=self.dialog_config.get('title', f"配置 {self.titleLabel.text()}"),
                    config_items=config_items,
                    description=self.dialog_config.get('description', ''),
                    parent=self.window()
                )
                
                if dialog.exec():
                    return dialog.getConfig()
                    
        except Exception as e:
            logger.error(f"Error showing dialog: {str(e)}")
            self._show_error_feedback(f"对话框错误: {str(e)}")
        
        return None
    
    def _show_success_feedback(self, message: str):
        """
        显示成功反馈
        
        Args:
            message (str): 成功信息
        """
        try:
            InfoBar.success(
                title="操作成功",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.parent() or self.window()
            )
        except Exception as e:
            logger.error(f"Failed to show success feedback: {str(e)}")
    
    def _show_error_feedback(self, message: str):
        """
        显示错误反馈
        
        Args:
            message (str): 错误信息
        """
        try:
            InfoBar.error(
                title="操作失败",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent() or self.window()
            )
        except Exception as e:
            logger.error(f"Failed to show error feedback: {str(e)}")
    
    def set_button_text(self, text: str):
        """
        Update button text
        
        Args:
            text (str): New button text
        """
        self.button.setText(text)
    
    def set_button_enabled(self, enabled: bool):
        """
        Enable or disable the button
        
        Args:
            enabled (bool): Whether button should be enabled
        """
        self.button.setEnabled(enabled)