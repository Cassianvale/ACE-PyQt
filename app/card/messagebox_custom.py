#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generic Custom MessageBox Components
通用的自定义消息框组件，支持各种输入类型和配置场景
"""

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap, QDesktopServices, QFont
from qfluentwidgets import MessageBox, LineEdit, ComboBox, EditableComboBox, DateTimeEdit, BodyLabel, FluentStyleSheet, TextEdit
from typing import Optional, Dict, List, Union, Any
import datetime
import json


class MessageBoxImage(MessageBox):
    """Message box with image support"""
    def __init__(self, title: str, content: str, image: Optional[str | QPixmap], parent=None):
        super().__init__(title, content, parent)
        if image is not None:
            self.imageLabel = QLabel(parent)
            if isinstance(image, QPixmap):
                self.imageLabel.setPixmap(image)
            elif isinstance(image, str):
                self.imageLabel.setPixmap(QPixmap(image))
            else:
                raise ValueError("Unsupported image type.")
            self.imageLabel.setScaledContents(True)

            imageIndex = self.vBoxLayout.indexOf(self.textLayout) + 1
            self.vBoxLayout.insertWidget(imageIndex, self.imageLabel, 0, Qt.AlignCenter)


class MessageBoxSupport(MessageBoxImage):
    """Support/feedback message box with custom button text"""
    def __init__(self, title: str, content: str, image: str, button_text: str = "好的", parent=None):
        super().__init__(title, content, image, parent)

        self.yesButton.setText(button_text)
        self.cancelButton.setHidden(True)


class MessageBoxAnnouncement(MessageBoxImage):
    """Announcement message box with copyable content"""
    def __init__(self, title: str, content: str, image: Optional[str | QPixmap], 
                 button_text: str = "收到", copyable: bool = True, parent=None):
        super().__init__(title, content, image, parent)

        self.yesButton.setText(button_text)
        self.cancelButton.setHidden(True)
        if copyable:
            self.setContentCopyable(True)


class MessageBoxHtml(MessageBox):
    """Message box with HTML content and link support"""
    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content, parent)

        self.buttonLayout.removeWidget(self.yesButton)
        self.buttonLayout.removeWidget(self.cancelButton)
        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.contentLabel = BodyLabel(content, parent)
        self.contentLabel.setObjectName("contentLabel")
        self.contentLabel.setOpenExternalLinks(True)
        self.contentLabel.linkActivated.connect(self.open_url)
        self.contentLabel.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        FluentStyleSheet.DIALOG.apply(self.contentLabel)

        self.buttonLayout.addWidget(self.cancelButton, 1, Qt.AlignVCenter)
        self.buttonLayout.addWidget(self.yesButton, 1, Qt.AlignVCenter)
        self.textLayout.addWidget(self.contentLabel, 0, Qt.AlignTop)

    def open_url(self, url):
        QDesktopServices.openUrl(QUrl(url))


class MessageBoxUpdate(MessageBoxHtml):
    """Update notification message box with custom button text"""
    def __init__(self, title: str, content: str, 
                 yes_text: str = "下载", cancel_text: str = "稍后", parent=None):
        super().__init__(title, content, parent)

        self.yesButton.setText(yes_text)
        self.cancelButton.setText(cancel_text)


class MessageBoxDisclaimer(MessageBoxHtml):
    """Disclaimer message box with customizable button text"""
    def __init__(self, title: str, content: str, 
                 yes_text: str = "拒绝", cancel_text: str = "接受",
                 copyable: bool = True, parent=None):
        super().__init__(title, content, parent)

        self.yesButton.setText(yes_text)
        self.cancelButton.setText(cancel_text)
        if copyable:
            self.setContentCopyable(True)


class MessageBoxEdit(MessageBox):
    """Single-line text input dialog"""
    def __init__(self, title: str, content: str = "", placeholder: str = "",
                 yes_text: str = "确认", cancel_text: str = "取消", parent=None):
        super().__init__(title, "", parent)

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText(yes_text)
        self.cancelButton.setText(cancel_text)

        self.lineEdit = LineEdit(self)
        self.lineEdit.setText(content)
        if placeholder:
            self.lineEdit.setPlaceholderText(placeholder)
        self.textLayout.addWidget(self.lineEdit, 0, Qt.AlignTop)

        self.buttonGroup.setMinimumWidth(480)

    def getText(self):
        return self.lineEdit.text()


class MessageBoxEditMultiple(MessageBox):
    """Multi-line text input dialog"""
    def __init__(self, title: str, content: str = "", placeholder: str = "",
                 height: int = 250, yes_text: str = "确认", cancel_text: str = "取消", parent=None):
        super().__init__(title, "", parent)

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText(yes_text)
        self.cancelButton.setText(cancel_text)

        self.textEdit = TextEdit(self)
        self.textEdit.setFixedHeight(height)
        self.textEdit.setText(content)
        if placeholder:
            self.textEdit.setPlaceholderText(placeholder)
        self.textLayout.addWidget(self.textEdit, 0, Qt.AlignTop)

        self.buttonGroup.setMinimumWidth(480)

    def getText(self):
        return self.textEdit.toPlainText()
    
    def getLines(self):
        """Get text as list of lines"""
        return self.getText().splitlines()


class MessageBoxDate(MessageBox):
    """Date/time picker dialog"""
    def __init__(self, title: str, content: datetime.datetime = None, 
                 yes_text: str = "确认", cancel_text: str = "取消", parent=None):
        super().__init__(title, "", parent)

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText(yes_text)
        self.cancelButton.setText(cancel_text)

        self.datePicker = DateTimeEdit(self)
        if content:
            self.datePicker.setDateTime(content)

        self.textLayout.addWidget(self.datePicker, 0, Qt.AlignTop)

        self.buttonGroup.setMinimumWidth(480)

    def getDateTime(self):
        return self.datePicker.dateTime().toPyDateTime()


class MessageBoxCombo(MessageBox):
    """Combo box selection dialog"""
    def __init__(self, title: str, options: List[str], current: str = "",
                 description: str = "", yes_text: str = "确认", cancel_text: str = "取消", parent=None):
        super().__init__(title, "", parent)

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText(yes_text)
        self.cancelButton.setText(cancel_text)

        self.buttonGroup.setMinimumWidth(480)

        # 添加描述文本
        if description:
            self.descLabel = QLabel(description, self)
            self.descLabel.setWordWrap(True)
            self.textLayout.addWidget(self.descLabel, 0, Qt.AlignTop)

        # 创建下拉框
        self.comboBox = ComboBox(self)
        self.comboBox.addItems(options)
        
        # 设置当前值
        if current and current in options:
            self.comboBox.setCurrentText(current)

        self.textLayout.addWidget(self.comboBox, 0, Qt.AlignTop)

    def getSelectedText(self):
        return self.comboBox.currentText()
    
    def getSelectedIndex(self):
        return self.comboBox.currentIndex()


class MessageBoxKeyBind(MessageBox):
    """Key binding input dialog"""
    def __init__(self, title: str, current_key: str = "",
                 yes_text: str = "确认", cancel_text: str = "取消", parent=None):
        super().__init__(title, "", parent)

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText(yes_text)
        self.cancelButton.setText(cancel_text)

        self.keyInput = LineEdit(self)
        self.keyInput.setText(current_key)
        self.keyInput.setPlaceholderText("按下组合键...")
        self.keyInput.setReadOnly(True)
        
        # 添加说明
        self.infoLabel = QLabel("点击输入框后按下想要设置的组合键", self)
        self.infoLabel.setStyleSheet("color: gray; font-size: 12px;")
        
        self.textLayout.addWidget(self.infoLabel, 0, Qt.AlignTop)
        self.textLayout.addWidget(self.keyInput, 0, Qt.AlignTop)

        self.buttonGroup.setMinimumWidth(480)

        # 键盘事件处理
        self.keyInput.keyPressEvent = self._keyPressEvent

    def _keyPressEvent(self, event):
        """处理按键事件"""
        modifiers = []
        
        if event.modifiers() & Qt.ControlModifier:
            modifiers.append("Ctrl")
        if event.modifiers() & Qt.AltModifier:
            modifiers.append("Alt")
        if event.modifiers() & Qt.ShiftModifier:
            modifiers.append("Shift")
        if event.modifiers() & Qt.MetaModifier:
            modifiers.append("Meta")
        
        key = event.key()
        key_name = ""
        
        # 处理特殊键
        if key == Qt.Key_Space:
            key_name = "Space"
        elif key == Qt.Key_Tab:
            key_name = "Tab"
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            key_name = "Enter"
        elif key == Qt.Key_Escape:
            key_name = "Esc"
        elif key >= Qt.Key_F1 and key <= Qt.Key_F24:
            key_name = f"F{key - Qt.Key_F1 + 1}"
        elif key >= Qt.Key_0 and key <= Qt.Key_9:
            key_name = chr(key)
        elif key >= Qt.Key_A and key <= Qt.Key_Z:
            key_name = chr(key)
        else:
            key_name = event.text().upper()
        
        if key_name:
            key_combo = "+".join(modifiers + [key_name])
            self.keyInput.setText(key_combo)

    def getKey(self):
        return self.keyInput.text()


class MessageBoxConfig(MessageBox):
    """Generic configuration dialog with multiple input fields"""
    def __init__(self, title: str, config_items: Dict[str, Dict], 
                 description: str = "", yes_text: str = "确认", cancel_text: str = "取消", parent=None):
        super().__init__(title, "", parent)
        self.config_items = config_items

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText(yes_text)
        self.cancelButton.setText(cancel_text)

        self.buttonGroup.setMinimumWidth(480)

        font = QFont()
        font.setPointSize(10)
        self.textLayout.setSpacing(4)

        self.input_widgets = {}
        
        for field_name, field_config in config_items.items():
            # 字段标题
            titleLabel = QLabel(field_name, self)
            titleLabel.setFont(font)
            self.textLayout.addWidget(titleLabel, 0, Qt.AlignTop)

            # 根据字段类型创建对应的输入控件
            field_type = field_config.get('type', 'text')
            default_value = field_config.get('default', '')
            options = field_config.get('options', [])
            
            if field_type == 'combo' and options:
                widget = ComboBox(self)
                widget.addItems(options)
                if default_value in options:
                    widget.setCurrentText(str(default_value))
            elif field_type == 'multiline':
                widget = TextEdit(self)
                widget.setFixedHeight(100)
                widget.setText(str(default_value))
            else:  # 默认为文本输入
                widget = LineEdit(self)
                widget.setText(str(default_value))
                placeholder = field_config.get('placeholder', '')
                if placeholder:
                    widget.setPlaceholderText(placeholder)
            
            widget.setFont(font)
            self.textLayout.addWidget(widget, 0, Qt.AlignTop)
            self.input_widgets[field_name] = widget

        # 添加描述信息
        if description:
            self.titleLabelInfo = QLabel(description, self)
            self.titleLabelInfo.setWordWrap(True)
            self.textLayout.addWidget(self.titleLabelInfo, 0, Qt.AlignTop)
    
    def getConfig(self):
        """Get all configuration values"""
        result = {}
        for field_name, widget in self.input_widgets.items():
            if isinstance(widget, LineEdit):
                result[field_name] = widget.text()
            elif isinstance(widget, TextEdit):
                result[field_name] = widget.toPlainText()
            elif isinstance(widget, ComboBox):
                result[field_name] = widget.currentText()
        return result


class MessageBoxFormFields(MessageBox):
    """Dynamic form fields dialog"""
    def __init__(self, title: str, fields: Dict[str, str], 
                 description: str = "", yes_text: str = "确认", cancel_text: str = "取消", parent=None):
        super().__init__(title, "", parent)
        self.fields = fields

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText(yes_text)
        self.cancelButton.setText(cancel_text)

        self.buttonGroup.setMinimumWidth(480)

        font = QFont()
        font.setPointSize(10)
        self.textLayout.setSpacing(4)

        self.lineEdit_dict = {}
        for field_name, default_value in fields.items():
            titleLabel = QLabel(field_name, self)
            titleLabel.setFont(font)
            self.textLayout.addWidget(titleLabel, 0, Qt.AlignTop)

            lineEdit = LineEdit(self)
            lineEdit.setText(str(default_value))
            lineEdit.setFont(font)

            self.textLayout.addWidget(lineEdit, 0, Qt.AlignTop)
            self.lineEdit_dict[field_name] = lineEdit

        # 添加描述信息
        if description:
            self.titleLabelInfo = QLabel(description, self)
            self.titleLabelInfo.setWordWrap(True)
            self.textLayout.addWidget(self.titleLabelInfo, 0, Qt.AlignTop)
    
    def getFields(self):
        """Get all field values"""
        return {field_name: lineEdit.text() for field_name, lineEdit in self.lineEdit_dict.items()}


class MessageBoxPairList(MessageBox):
    """Dialog for managing key-value pairs"""
    def __init__(self, title: str, pairs: List[tuple], max_pairs: int = 6,
                 key_label: str = "键", value_label: str = "值",
                 description: str = "", yes_text: str = "确认", cancel_text: str = "取消", parent=None):
        super().__init__(title, "", parent)
        self.pairs = pairs
        self.max_pairs = max_pairs

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText(yes_text)
        self.cancelButton.setText(cancel_text)

        self.buttonGroup.setMinimumWidth(400)

        font = QFont()
        font.setPointSize(12)

        self.input_pairs = []
        for i in range(max_pairs):
            key_value = pairs[i] if i < len(pairs) else ("", "")
            
            keyInput = LineEdit(self)
            keyInput.setMaximumWidth(150)
            keyInput.setText(str(key_value[0]))
            keyInput.setPlaceholderText(key_label)

            valueInput = LineEdit(self)
            valueInput.setMaximumWidth(150)
            valueInput.setText(str(key_value[1]))
            valueInput.setPlaceholderText(value_label)

            horizontalLayout = QHBoxLayout()
            horizontalLayout.addWidget(keyInput)
            horizontalLayout.addWidget(valueInput)
            self.textLayout.addLayout(horizontalLayout)

            self.input_pairs.append((keyInput, valueInput))

        # 添加描述信息
        if description:
            self.titleLabelInfo = QLabel(description, self)
            self.titleLabelInfo.setWordWrap(True)
            self.textLayout.addWidget(self.titleLabelInfo, 0, Qt.AlignTop)
    
    def getPairs(self):
        """Get all key-value pairs (excluding empty ones)"""
        result = []
        for key_input, value_input in self.input_pairs:
            key = key_input.text().strip()
            value = value_input.text().strip()
            if key or value:  # 只要有一个不为空就保存
                result.append((key, value))
        return result