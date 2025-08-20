#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Push Setting Card - Action button configuration card with business logic integration
"""


from qfluentwidgets import SettingCard, FluentIconBase, InfoBar, InfoBarPosition
from typing import Union
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
from utils.logger import logger


class PushSettingCard(SettingCard):
    """
    Enhanced Push Setting Card with business logic integration
    """
    
    # 按钮点击信号
    actionRequested = pyqtSignal()
    
    def __init__(self, text, icon: Union[str, QIcon, FluentIconBase], title, content=None, business_handler=None, parent=None):
        """
        Initialize push setting card
        
        Args:
            text (str): Button text
            icon: Card icon
            title (str): Card title
            content (str, optional): Card description
            business_handler (callable, optional): Business logic handler function
            parent: Parent widget
        """
        super().__init__(text, icon, title, content, parent)
           
        self.business_handler = business_handler
        
        # Connect internal signal
        self.clicked.connect(self._on_clicked)

    def set_business_handler(self, handler):
        """
        Set the business logic handler
        
        Args:
            handler (callable): Function to handle business logic
        """
        self.business_handler = handler
    
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
    
    def _on_clicked(self):
        """
        Handle button click
        """
        try:
            # Call business logic handler if provided
            if self.business_handler:
                self.business_handler()
            
            # Emit action requested signal
            self.actionRequested.emit()
            logger.debug(f"Action requested for {self.titleLabel.text()}")
            
        except Exception as e:
            logger.error(f"Error handling action for {self.titleLabel.text()}: {str(e)}")