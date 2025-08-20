# coding: utf-8
from enum import Enum

from qfluentwidgets import StyleSheetBase, Theme, qconfig


class StyleSheet(StyleSheetBase, Enum):
    """ Style sheet  """

    HOME_INTERFACE = "home_interface"
    HELP_INTERFACE = "help_interface"
    CHANGELOGS_INTERFACE = "changelogs_interface"
    SETTINGS_INTERFACE = "settings_interface"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f"./assets/theme/{theme.value.lower()}/{self.value}.qss"
