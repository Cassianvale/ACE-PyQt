#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
窗口行为设置业务逻辑
"""

from utils.logger import logger
from module.config import cfg


class WindowSettings:
    """窗口行为设置业务逻辑"""
    
    @staticmethod
    def set_close_behavior(close_to_tray: bool) -> bool:
        """
        设置窗口关闭行为
        
        Args:
            close_to_tray (bool): 是否关闭到系统托盘
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 更新配置
            cfg.close_to_tray = close_to_tray
            
            # 保存配置
            if cfg.save_config():
                logger.debug(f"关闭行为设置已保存: {'最小化到后台' if close_to_tray else '直接退出'}")
                return True
            else:
                logger.warning(f"关闭行为设置已更改但保存失败: {'最小化到后台' if close_to_tray else '直接退出'}")
                return False
                
        except Exception as e:
            logger.error(f"设置关闭行为失败: {str(e)}")
            return False
    
    @staticmethod
    def get_close_behavior() -> bool:
        """
        获取当前关闭行为设置
        
        Returns:
            bool: 是否关闭到系统托盘
        """
        return cfg.close_to_tray
    
    @staticmethod
    def save_window_size(width: int, height: int) -> bool:
        """
        保存窗口尺寸
        
        Args:
            width (int): 窗口宽度
            height (int): 窗口高度
            
        Returns:
            bool: 操作是否成功
        """
        try:
            return cfg.save_window_size(width, height)
        except Exception as e:
            logger.error(f"保存窗口尺寸失败: {str(e)}")
            return False
    
    @staticmethod
    def get_window_size() -> tuple[int, int]:
        """
        获取保存的窗口尺寸
        
        Returns:
            tuple[int, int]: (宽度, 高度)
        """
        return cfg.get_window_size()