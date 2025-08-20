#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志和调试设置业务逻辑
"""

from app.tools import logger
from module.config import cfg


class LoggingSettings:
    """日志和调试设置业务逻辑"""
    
    @staticmethod
    def toggle_debug_mode(enabled: bool) -> bool:
        """
        切换调试模式
        
        Args:
            enabled (bool): 是否启用调试模式
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 更新配置
            cfg.debug_mode = enabled
            
            # 保存配置
            if cfg.save_config():
                logger.debug(f"调试模式设置已保存: {'开启' if enabled else '关闭'}")
                
                # 重新初始化日志系统
                LoggingSettings._reinitialize_logger()
                
                return True
            else:
                logger.warning(f"调试模式已更改但保存失败: {'开启' if enabled else '关闭'}")
                return False
                
        except Exception as e:
            logger.error(f"切换调试模式失败: {str(e)}")
            return False
    
    @staticmethod
    def get_debug_mode_status() -> bool:
        """
        获取当前调试模式状态
        
        Returns:
            bool: 当前调试模式状态
        """
        return cfg.debug_mode
    
    @staticmethod
    def _reinitialize_logger():
        """重新初始化日志系统"""
        try:
            from app.tools import setup_logger
            
            setup_logger(
                log_dir=cfg.log_dir,
                log_retention_days=cfg.log_retention_days,
                log_rotation=cfg.log_rotation,
                debug_mode=cfg.debug_mode,
            )
            logger.info(f"日志系统已重新初始化，调试模式: {'开启' if cfg.debug_mode else '关闭'}")
            
        except Exception as e:
            logger.error(f"重新初始化日志系统失败: {str(e)}")
    
    @staticmethod
    def get_log_settings() -> dict:
        """
        获取日志相关设置
        
        Returns:
            dict: 日志设置信息
        """
        return {
            'debug_mode': cfg.debug_mode,
            'log_dir': str(cfg.log_dir),
            'log_retention_days': cfg.log_retention_days,
            'log_rotation': cfg.log_rotation
        }