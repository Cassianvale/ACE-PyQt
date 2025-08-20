#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主题设置业务逻辑
"""

from utils.logger import logger
from module.config import cfg


class ThemeManager:
    """主题管理业务逻辑"""
    
    @staticmethod
    def switch_theme(theme: str) -> bool:
        """
        切换应用程序主题
        
        Args:
            theme (str): 主题类型，可以是 "light", "dark" 或 "auto"
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 验证主题参数
            if theme not in ["light", "dark", "auto"]:
                logger.error(f"无效的主题类型: {theme}")
                return False
                
            # 检查是否需要切换
            if theme == cfg.theme:
                logger.debug(f"主题未发生变化: {theme}")
                return True
                
            # 更新配置
            cfg.theme = theme
            
            # 保存配置
            if cfg.save_config():
                logger.debug(f"主题设置已保存: {theme}")
                return True
            else:
                logger.warning(f"主题设置保存失败: {theme}")
                return False
                
        except Exception as e:
            logger.error(f"切换主题失败: {str(e)}")
            return False
    
    @staticmethod
    def get_current_theme() -> str:
        """
        获取当前主题
        
        Returns:
            str: 当前主题类型
        """
        return cfg.theme
    
    @staticmethod
    def get_theme_display_name(theme: str = None) -> str:
        """
        获取主题的显示名称
        
        Args:
            theme (str, optional): 主题类型，如果不提供则使用当前主题
            
        Returns:
            str: 主题的显示名称
        """
        if theme is None:
            theme = cfg.theme
            
        theme_names = {
            "light": "浅色",
            "dark": "深色",
            "auto": "自动"
        }
        
        return theme_names.get(theme, "未知")
    
    @staticmethod
    def get_available_themes() -> list[str]:
        """
        获取可用的主题列表
        
        Returns:
            list[str]: 可用主题列表
        """
        return ["light", "dark", "auto"]