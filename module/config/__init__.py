#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration module initialization following March7thAssistant pattern.
Creates a singleton configuration instance for the entire application.
"""

from config.config_manager import ConfigManager

# Create singleton configuration instance
cfg = ConfigManager()

# Export the configuration instance
__all__ = ['cfg']