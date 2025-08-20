#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Combo Box Setting Card - Selection configuration card with business logic integration
"""

from qfluentwidgets import ComboBoxSettingCard as BaseComboBoxSettingCard
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout
from utils.logger import logger


class ComboBoxSettingCard(BaseComboBoxSettingCard):
    """
    Enhanced ComboBox Setting Card with automatic business logic binding
    """
    
    # 设置值变化信号
    valueChanged = pyqtSignal(str)
    
    def __init__(self, icon, title, content=None, texts=None, business_handler=None, parent=None):
        """
        Initialize combo box setting card
        
        Args:
            icon: Card icon
            title (str): Card title
            content (str, optional): Card description
            texts (list, optional): List of option texts
            business_handler (callable, optional): Business logic handler function
            parent: Parent widget
        """
        super().__init__(icon, title, content, texts or [], parent)
        
        self.business_handler = business_handler
        self._initializing = False
        self._option_mapping = {}  # Maps display text to actual values
        
        # Connect internal signal
        self.comboBox.currentTextChanged.connect(self._on_text_changed)
    
    def set_business_handler(self, handler):
        """
        Set the business logic handler
        
        Args:
            handler (callable): Function to handle business logic
        """
        self.business_handler = handler
    
    def set_options(self, options):
        """
        Set available options
        
        Args:
            options (list or dict): List of option strings, or dict mapping values to display text
        """
        self.comboBox.clear()
        
        if isinstance(options, dict):
            self._option_mapping = {v: k for k, v in options.items()}
            for value, display_text in options.items():
                self.comboBox.addItem(display_text, value)
        else:
            self._option_mapping = {}
            for option in options:
                self.comboBox.addItem(option, option)
    
    def load_value(self, value: str):
        """
        Load value from configuration (without triggering business logic)
        
        Args:
            value (str): Configuration value
        """
        self._initializing = True
        try:
            # Find the correct display text for the value
            for i in range(self.comboBox.count()):
                if self.comboBox.itemData(i) == value:
                    self.comboBox.setCurrentIndex(i)
                    logger.debug(f"Loaded value for {self.titleLabel.text()}: {value}")
                    return
            
            # If exact match not found, try setting by text
            if value in self._option_mapping:
                self.comboBox.setCurrentText(self._option_mapping[value])
            else:
                self.comboBox.setCurrentText(value)
                
        finally:
            self._initializing = False
    
    def get_value(self):
        """
        Get current value
        
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
        Handle text change
        
        Args:
            text (str): New selected text
        """
        # Skip if we're initializing
        if self._initializing:
            return
        
        try:
            # Get the actual value
            current_value = self.get_value()
            
            # Call business logic handler if provided
            if self.business_handler:
                success = self.business_handler(current_value)
                if not success:
                    # Revert if business logic failed
                    return
            
            # Emit value changed signal
            self.valueChanged.emit(current_value)
            logger.debug(f"Setting changed for {self.titleLabel.text()}: {current_value}")
            
        except Exception as e:
            logger.error(f"Error handling setting change for {self.titleLabel.text()}: {str(e)}")