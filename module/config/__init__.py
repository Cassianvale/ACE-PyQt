#!/usr/bin/env python
# -*- coding: utf-8 -*-

from module.config.app_config import APP_INFO, DEFAULT_CONFIG, SYSTEM_CONFIG
from module.config.config_manager import ConfigManager

# Create singleton configuration instance
cfg = ConfigManager()

__all__ = ["ConfigManager", "APP_INFO", "DEFAULT_CONFIG", "SYSTEM_CONFIG", "cfg"]