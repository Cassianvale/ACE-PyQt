#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qfluentwidgets import setTheme, Theme, qconfig
from module.config import cfg


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
            return False

        cls._apply_theme(theme)

        cfg.theme = theme
        if cfg.save_config():
            return True
        else:
            return False

    @classmethod
    def apply_theme_from_config(cls):
        current_theme = cls.get_current_theme()
        cls._apply_theme(current_theme)

    @classmethod
    def get_theme_display_name(cls, theme):
        return cls.THEMES.get(theme, {}).get("display", theme)

    @classmethod
    def get_current_fluent_theme(cls):
        return getattr(qconfig, 'theme', Theme.AUTO)

    @classmethod
    def get_available_themes(cls):
        return {theme_id: config["display"] for theme_id, config in cls.THEMES.items()}
    
    @classmethod
    def _is_valid_theme(cls, theme):
        return theme in cls.THEMES

    @classmethod
    def _apply_theme(cls, theme):
        fluent_theme = cls.THEMES[theme]["enum"]
        setTheme(fluent_theme, lazy=True)