#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
通知设置业务逻辑
"""

from utils.logger import logger
from module.config import cfg


class NotificationSettings:
    """通知设置业务逻辑"""
    
    @staticmethod
    def toggle_notifications(enabled: bool) -> bool:
        """
        切换通知开关
        
        Args:
            enabled (bool): 是否启用通知
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 更新配置
            cfg.show_notifications = enabled
            
            # 保存配置
            if cfg.save_config():
                logger.debug(f"通知设置已保存: {'开启' if enabled else '关闭'}")
                return True
            else:
                logger.warning(f"通知状态已更改但保存失败: {'开启' if enabled else '关闭'}")
                return False
                
        except Exception as e:
            logger.error(f"切换通知设置失败: {str(e)}")
            return False
    
    @staticmethod
    def get_notification_status() -> bool:
        """
        获取当前通知状态
        
        Returns:
            bool: 当前通知状态
        """
        return cfg.show_notifications