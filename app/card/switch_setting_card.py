#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Switch Setting Card - Boolean configuration card that automatically binds to business logic
"""

from qfluentwidgets import SwitchSettingCard as BaseSwitchSettingCard
from PyQt5.QtCore import pyqtSignal
from utils.logger import logger


class SwitchSettingCard(BaseSwitchSettingCard):
    """
    Enhanced Switch Setting Card with automatic business logic binding
    """
    
    # 设置值变化信号
    valueChanged = pyqtSignal(bool)
    
    def __init__(self, icon, title, content=None, business_handler=None, parent=None):
        """
        Initialize switch setting card
        
        Args:
            icon: Card icon
            title (str): Card title
            content (str, optional): Card description
            business_handler (callable, optional): Business logic handler function
            parent: Parent widget
        """
        super().__init__(icon, title, content, parent)
        
        self.business_handler = business_handler
        self._initializing = False
        
        # Connect internal signal
        self.switchButton.checkedChanged.connect(self._on_checked_changed)
    
    def set_business_handler(self, handler):
        """
        Set the business logic handler
        
        Args:
            handler (callable): Function to handle business logic
        """
        self.business_handler = handler
    
    def load_value(self, value: bool):
        """
        Load value from configuration (without triggering business logic)
        
        Args:
            value (bool): Configuration value
        """
        self._initializing = True
        try:
            self.switchButton.setChecked(value)
            logger.debug(f"Loaded value for {self.titleLabel.text()}: {value}")
        finally:
            self._initializing = False
    
    def get_value(self) -> bool:
        """
        Get current value
        
        Returns:
            bool: Current switch state
        """
        return self.switchButton.isChecked()
    
    def _on_checked_changed(self, checked: bool):
        """
        Handle check state change
        
        Args:
            checked (bool): New check state
        """
        # Skip if we're initializing
        if self._initializing:
            return
        
        try:
            # Call business logic handler if provided
            if self.business_handler:
                success = self.business_handler(checked)
                if not success:
                    # Revert if business logic failed
                    self._initializing = True
                    try:
                        self.switchButton.setChecked(not checked)
                    finally:
                        self._initializing = False
                    return
            
            # Emit value changed signal
            self.valueChanged.emit(checked)
            logger.debug(f"Setting changed for {self.titleLabel.text()}: {checked}")
            
        except Exception as e:
            logger.error(f"Error handling setting change for {self.titleLabel.text()}: {str(e)}")
            # Revert on error
            self._initializing = True
            try:
                self.switchButton.setChecked(not checked)
            finally:
                self._initializing = False