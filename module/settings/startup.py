#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app.tools import logger, enable_auto_start, disable_auto_start
from module.config import cfg


class StartupSettings:
    """开机自启动设置业务逻辑"""
    
    @staticmethod
    def toggle_auto_start(enabled: bool, app_name: str) -> bool:
        """
        切换开机自启动状态
        
        Args:
            enabled (bool): 是否启用开机自启动
            app_name (str): 应用程序名称
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 更新配置
            cfg.auto_start = enabled
            
            # 修改注册表
            if enabled:
                enable_auto_start(app_name)
                logger.info(f"已启用开机自启动: {app_name}")
            else:
                disable_auto_start(app_name)
                logger.info(f"已禁用开机自启动: {app_name}")
            
            # 保存配置
            if cfg.save_config():
                logger.debug(f"开机自启状态已保存: {'开启' if enabled else '关闭'}")
                return True
            else:
                logger.warning(f"开机自启状态已更改但保存失败: {'开启' if enabled else '关闭'}")
                return False
                
        except Exception as e:
            logger.error(f"切换开机自启动失败: {str(e)}")
            return False
    
    @staticmethod
    def get_auto_start_status() -> bool:
        """
        获取当前开机自启动状态
        
        Returns:
            bool: 当前开机自启动状态
        """
        return cfg.auto_start
    
    @staticmethod
    def toggle_check_update_on_start(enabled: bool) -> bool:
        """
        切换启动时检查更新设置
        
        Args:
            enabled (bool): 是否启用启动时检查更新
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 更新配置
            cfg.check_update_on_start = enabled
            
            # 保存配置
            if cfg.save_config():
                logger.debug(f"启动时检查更新设置已保存: {'开启' if enabled else '关闭'}")
                return True
            else:
                logger.warning("启动时检查更新设置保存失败")
                return False
                
        except Exception as e:
            logger.error(f"切换启动时检查更新设置失败: {str(e)}")
            return False
    
    @staticmethod
    def get_check_update_on_start_status() -> bool:
        """
        获取启动时检查更新状态
        
        Returns:
            bool: 启动时检查更新状态
        """
        return cfg.check_update_on_start