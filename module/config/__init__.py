#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration module initialization following March7thAssistant pattern.
Creates a singleton configuration instance for the entire application.
"""

from module.config.config_manager import ConfigManager
from module.config.app_config import APP_INFO, DEFAULT_CONFIG, SYSTEM_CONFIG

# Create singleton configuration instance
cfg = ConfigManager()

# Export the configuration instance
__all__ = ["ConfigManager", "APP_INFO", "DEFAULT_CONFIG", "SYSTEM_CONFIG"] 