#!/usr/bin/env python
# -*- coding: utf-8 -*-


from app.tools.system_utils import run_as_admin, check_single_instance, enable_auto_start, disable_auto_start, check_auto_start
from app.tools.logger import logger, setup_logger
from app.tools.version_checker import get_version_checker, get_app_version, create_update_message, check_for_update
from app.tools.check_theme_change import checkThemeChange


__all__ = [
    "run_as_admin",
    "check_single_instance",
    "enable_auto_start",
    "disable_auto_start",
    "check_auto_start",
    "logger",
    "setup_logger",
    "get_version_checker",
    "get_app_version",
    "create_update_message",
    "check_for_update",
    "checkThemeChange",
]