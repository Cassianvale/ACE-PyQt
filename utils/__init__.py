#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""工具类模块"""

from utils.system_utils import run_as_admin, check_single_instance, enable_auto_start, disable_auto_start
from utils.logger import logger, setup_logger
from utils.notification import send_notification, create_notification_thread, find_icon_path
from utils.version_checker import get_version_checker, get_app_version, create_update_message, check_for_update


__all__ = [
    "run_as_admin",
    "check_single_instance",
    "enable_auto_start",
    "disable_auto_start",
    "logger",
    "setup_logger",
    "send_notification",
    "create_notification_thread",
    "find_icon_path",
    "get_version_checker",
    "get_app_version",
    "create_update_message",
    "check_for_update",
]
