#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qfluentwidgets import setTheme, Theme, qconfig
from module.config import cfg
from app.tools import logger


class ThemeManager:
    """主题管理器类"""

    # 主题配置
    THEMES = {
        "auto": {"enum": Theme.AUTO, "display": "跟随系统"},
        "light": {"enum": Theme.LIGHT, "display": "浅色模式"},
        "dark": {"enum": Theme.DARK, "display": "深色模式"}
    }

    @classmethod
    def get_current_theme(cls):
        return getattr(cfg, 'theme', 'auto')

    @classmethod
    def switch_theme(cls, theme):
        """
        切换主题并保存到配置

        Args:
            theme (str): 主题标识符 ('auto', 'light', 'dark')

        Returns:
            bool: 切换是否成功
        """
        # 验证主题有效性
        if not cls._is_valid_theme(theme):
            logger.error(f"无效的主题值: {theme}")
            return False

        try:
            # 应用主题
            cls._apply_theme(theme)

            # 保存配置
            cfg.theme = theme
            if cfg.save_config():
                logger.info(f"主题已切换为: {cls.get_theme_display_name(theme)}")
                return True
            else:
                logger.error("保存主题配置失败")
                return False

        except Exception as e:
            logger.error(f"切换主题失败: {str(e)}")
            return False

    @classmethod
    def apply_theme_from_config(cls):
        """从配置文件应用主题设置"""
        current_theme = cls.get_current_theme()
        try:
            cls._apply_theme(current_theme)
            logger.debug(f"已从配置应用主题: {cls.get_theme_display_name(current_theme)}")
        except Exception as e:
            logger.error(f"从配置应用主题失败: {str(e)}")

    @classmethod
    def get_theme_display_name(cls, theme):
        """获取主题的显示名称"""
        return cls.THEMES.get(theme, {}).get("display", theme)

    @classmethod
    def get_current_fluent_theme(cls):
        """获取当前的qFluentWidgets主题对象"""
        return getattr(qconfig, 'theme', Theme.AUTO)

    @classmethod
    def get_available_themes(cls):
        """获取可用的主题选项"""
        return {theme_id: config["display"] for theme_id, config in cls.THEMES.items()}
    
    @classmethod
    def _is_valid_theme(cls, theme):
        """验证主题是否有效"""
        return theme in cls.THEMES

    @classmethod
    def _apply_theme(cls, theme):
        """应用主题到qFluentWidgets"""
        fluent_theme = cls.THEMES[theme]["enum"]
        setTheme(fluent_theme, lazy=True)