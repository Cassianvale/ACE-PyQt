#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主题设置业务逻辑
Enhanced with system theme detection and automatic theme switching
"""

from app.tools import logger
from module.config import cfg
from qfluentwidgets import setTheme, Theme, qconfig
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import darkdetect


class SystemThemeListener(QThread):
    """
    System theme change listener thread
    Enhanced from check_theme_change.py with better integration
    """
    systemThemeChanged = pyqtSignal(str)  # Emit the detected theme
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._isSupported = False
        self._running = False
    
    def run(self):
        """Start listening for system theme changes"""
        try:
            # Test if system theme detection is supported
            current_theme = darkdetect.theme()
            if current_theme is None:
                logger.warning("System theme detection not supported on this platform")
                return
                
            self._isSupported = True
            self._running = True
            logger.debug("Starting system theme listener")
            
            # Start listening for theme changes
            darkdetect.listener(self._on_theme_changed)
            
        except (NotImplementedError, Exception) as e:
            logger.warning(f"System theme listener not supported: {str(e)}")
            self._isSupported = False
            self._running = False
    
    def _on_theme_changed(self, theme: str):
        """Handle system theme change"""
        if not self._running:
            return
            
        normalized_theme = theme.lower() if theme else "light"
        logger.debug(f"System theme changed to: {normalized_theme}")
        self.systemThemeChanged.emit(normalized_theme)
    
    def is_supported(self) -> bool:
        """Check if system theme detection is supported"""
        return self._isSupported
    
    def stop_listening(self):
        """Stop the theme listener"""
        self._running = False
        if self.isRunning():
            self.quit()
            self.wait(1000)  # Wait up to 1 second for thread to finish


class ThemeManager(QObject):
    """
    Enhanced theme management with system theme detection
    Integrated logic from check_theme_change.py
    """
    
    themeChanged = pyqtSignal(str)  # Emit when theme actually changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._theme_listener = None
        self._auto_theme_enabled = False
        self._switching_theme = False  # Recursion protection flag
        
        # Initialize system theme listener if auto theme is enabled
        if cfg.theme == "auto":
            self.enable_auto_theme()
    
    def enable_auto_theme(self):
        """Enable automatic theme detection"""
        if self._theme_listener is not None:
            return  # Already enabled
            
        try:
            self._theme_listener = SystemThemeListener(self)
            self._theme_listener.systemThemeChanged.connect(self._handle_system_theme_change)
            self._theme_listener.start()
            
            # Wait a moment for the thread to initialize
            self._theme_listener.wait(100)
            
            if self._theme_listener.is_supported():
                self._auto_theme_enabled = True
                logger.info("Auto theme detection enabled")
                
                # Apply current system theme immediately
                current_system_theme = self.get_system_theme()
                if current_system_theme:
                    self._apply_fluent_theme(current_system_theme)
            else:
                logger.warning("Auto theme not supported, falling back to light theme")
                self._cleanup_theme_listener()
                
        except Exception as e:
            logger.error(f"Failed to enable auto theme: {str(e)}")
            self._cleanup_theme_listener()
    
    def disable_auto_theme(self):
        """Disable automatic theme detection"""
        if self._theme_listener is None:
            return
            
        self._auto_theme_enabled = False
        self._cleanup_theme_listener()
        logger.info("Auto theme detection disabled")
    
    def _cleanup_theme_listener(self):
        """Clean up the theme listener thread"""
        if self._theme_listener is not None:
            self._theme_listener.stop_listening()
            self._theme_listener = None
    
    def _handle_system_theme_change(self, system_theme: str):
        """Handle system theme change when auto theme is enabled"""
        if not self._auto_theme_enabled or cfg.theme != "auto":
            return
            
        logger.debug(f"Applying system theme change: {system_theme}")
        self._apply_fluent_theme(system_theme)
        self.themeChanged.emit(system_theme)
    
    def _apply_fluent_theme(self, theme_name: str):
        """Apply theme to qfluentwidgets"""
        try:
            if theme_name.lower() == "dark":
                qconfig.theme = Theme.DARK
                setTheme(Theme.DARK, lazy=True)
            else:
                qconfig.theme = Theme.LIGHT  
                setTheme(Theme.LIGHT, lazy=True)
                
            logger.debug(f"Applied fluent theme: {theme_name}")
        except Exception as e:
            logger.error(f"Failed to apply fluent theme: {str(e)}")
    
    def get_system_theme(self) -> str:
        """Get current system theme"""
        try:
            system_theme = darkdetect.theme()
            return system_theme.lower() if system_theme else "light"
        except Exception as e:
            logger.warning(f"Failed to detect system theme: {str(e)}")
            return "light"
    
    def switch_theme(self, theme: str) -> bool:
        """
        切换应用程序主题 (Enhanced with system theme integration)
        
        Args:
            theme (str): 主题类型，可以是 "light", "dark" 或 "auto"
            
        Returns:
            bool: 操作是否成功
        """
        # Recursion protection
        if self._switching_theme:
            logger.debug(f"Theme switch already in progress, ignoring request for: {theme}")
            return True
            
        try:
            self._switching_theme = True
            
            # 验证主题参数
            if theme not in ["light", "dark", "auto"]:
                logger.error(f"无效的主题类型: {theme}")
                return False
                
            # 检查是否需要切换
            old_theme = cfg.theme
            if theme == old_theme:
                logger.debug(f"主题未发生变化: {theme}")
                return True
            
            # 处理从auto主题切换的情况
            if old_theme == "auto":
                self.disable_auto_theme()
            
            # 更新配置
            cfg.theme = theme
            
            # 应用主题
            if theme == "auto":
                self.enable_auto_theme()
            else:
                # 直接应用指定主题
                self._apply_fluent_theme(theme)
            
            # 保存配置
            if cfg.save_config():
                logger.info(f"主题已切换: {old_theme} -> {theme}")
                # Only emit signal if we successfully switched
                if old_theme != theme:
                    self.themeChanged.emit(theme)
                return True
            else:
                logger.warning(f"主题设置保存失败: {theme}")
                # 回滚主题设置
                cfg.theme = old_theme
                if old_theme == "auto":
                    self.enable_auto_theme()
                else:
                    self._apply_fluent_theme(old_theme)
                return False
                
        except Exception as e:
            logger.error(f"切换主题失败: {str(e)}")
            return False
        finally:
            # Always clear the recursion protection flag
            self._switching_theme = False
    
    def get_current_theme(self) -> str:
        """
        获取当前配置的主题
        
        Returns:
            str: 当前主题类型
        """
        return cfg.theme
    
    def get_effective_theme(self) -> str:
        """
        获取当前有效的主题 (如果是auto则返回实际应用的主题)
        
        Returns:
            str: 当前有效的主题类型
        """
        if cfg.theme == "auto":
            return self.get_system_theme()
        return cfg.theme
    
    def is_auto_theme_supported(self) -> bool:
        """
        检查是否支持自动主题检测
        
        Returns:
            bool: 是否支持自动主题
        """
        try:
            return darkdetect.theme() is not None
        except Exception:
            return False
    
    def is_auto_theme_enabled(self) -> bool:
        """
        检查自动主题是否已启用
        
        Returns:
            bool: 自动主题是否已启用
        """
        return self._auto_theme_enabled and cfg.theme == "auto"
    
    def cleanup(self):
        """Clean up resources when shutting down"""
        if self._theme_listener is not None:
            self.disable_auto_theme()
    
    # Static utility methods for backward compatibility
    @staticmethod
    def get_current_theme_static() -> str:
        """
        获取当前主题 (静态方法，向后兼容)
        
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


# Global theme manager instance for easy access
_theme_manager_instance = None

def get_theme_manager(parent=None) -> ThemeManager:
    """
    Get the global theme manager instance (Singleton pattern)
    
    Args:
        parent: Parent QObject for the theme manager
        
    Returns:
        ThemeManager: Global theme manager instance
    """
    global _theme_manager_instance
    if _theme_manager_instance is None:
        _theme_manager_instance = ThemeManager(parent)
    return _theme_manager_instance

def cleanup_theme_manager():
    """Clean up the global theme manager instance"""
    global _theme_manager_instance
    if _theme_manager_instance is not None:
        _theme_manager_instance.cleanup()
        _theme_manager_instance = None


# Backward compatibility wrapper functions
class ThemeManagerCompat:
    """
    Backward compatibility wrapper for static method usage
    Automatically uses the enhanced theme manager when needed
    """
    
    @staticmethod
    def switch_theme(theme: str) -> bool:
        """
        切换应用程序主题 (兼容性包装器)
        自动使用增强的主题管理器
        """
        theme_manager = get_theme_manager()
        return theme_manager.switch_theme(theme)
    
    @staticmethod
    def get_current_theme() -> str:
        """获取当前主题 (兼容性包装器)"""
        return cfg.theme
    
    @staticmethod
    def get_theme_display_name(theme: str = None) -> str:
        """获取主题显示名称 (兼容性包装器)"""
        # Store the original static method reference to avoid recursion
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
        """获取可用主题列表 (兼容性包装器)"""
        return ["light", "dark", "auto"]


# Store original static methods before overriding
_original_switch_theme = ThemeManager.switch_theme
_original_get_current_theme = ThemeManager.get_current_theme_static

# Override the original ThemeManager static methods for backward compatibility
# This allows existing code to continue working without changes
ThemeManager.switch_theme = staticmethod(ThemeManagerCompat.switch_theme)
ThemeManager.get_current_theme = staticmethod(ThemeManagerCompat.get_current_theme)