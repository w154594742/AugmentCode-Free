#!/usr/bin/env python3
"""
PyQt6欢迎页面
替代原有的Tkinter欢迎页面
"""

import webbrowser
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap

from .components import (
    TitleLabel, SubtitleLabel, SecondaryLabel, LinkLabel, 
    ModernButton, WarningFrame, ScrollableFrame
)
from .font_manager import get_default_font
from language_manager import get_language_manager, get_text


class WelcomePage(QWidget):
    """PyQt6欢迎页面"""
    
    continue_clicked = pyqtSignal()
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.language_manager = get_language_manager(config_manager)
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """设置用户界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(15)
        
        # 创建滚动区域
        scroll_area = ScrollableFrame()
        main_layout.addWidget(scroll_area)
        
        # 标题区域
        self._create_title_section(scroll_area)
        
        # 语言选择区域
        self._create_language_section(scroll_area)
        
        # 欢迎信息区域
        self._create_welcome_section(scroll_area)
        
        # 警告信息区域
        self._create_warning_section(scroll_area)
        
        # GitHub链接区域
        self._create_github_section(scroll_area)
        
        # 继续按钮
        self._create_continue_section(scroll_area)
        
        # 添加弹性空间
        scroll_area.add_stretch()
    
    def _create_title_section(self, parent):
        """创建标题区域"""
        # 主标题
        self.title_label = TitleLabel(get_text("app.title"))
        parent.add_widget(self.title_label)
        
        # 欢迎副标题
        self.welcome_title = SubtitleLabel(get_text("dialogs.titles.welcome_title"))
        parent.add_widget(self.welcome_title)
    
    def _create_language_section(self, parent):
        """创建语言选择区域"""
        # 语言标签
        self.lang_label = SecondaryLabel(get_text("app.language"))
        parent.add_widget(self.lang_label)
        
        # 语言选择下拉框
        self.language_combo = QComboBox()
        self.language_combo.setFont(get_default_font(10))
        
        # 填充语言选项
        available_langs = self.language_manager.get_available_languages()
        lang_values = list(available_langs.values())
        self.language_combo.addItems(lang_values)
        
        # 设置当前语言
        current_lang = self.language_manager.get_language()
        current_display = available_langs.get(current_lang, lang_values[0])
        current_index = lang_values.index(current_display) if current_display in lang_values else 0
        self.language_combo.setCurrentIndex(current_index)
        
        parent.add_widget(self.language_combo)
    
    def _create_welcome_section(self, parent):
        """创建欢迎信息区域"""
        welcome_text = get_text("dialogs.messages.welcome_message")
        self.welcome_message = SecondaryLabel(welcome_text)
        self.welcome_message.setWordWrap(True)
        parent.add_widget(self.welcome_message)
    
    def _create_warning_section(self, parent):
        """创建警告信息区域"""
        warning_text = get_text("dialogs.messages.first_run_warning")
        warning_frame = WarningFrame(warning_text)
        parent.add_widget(warning_frame)
    
    def _create_github_section(self, parent):
        """创建GitHub链接区域"""
        self.github_label = LinkLabel(get_text("copyright.github"))
        parent.add_widget(self.github_label)
    
    def _create_continue_section(self, parent):
        """创建继续按钮区域"""
        continue_text = f"{get_text('buttons.ok')} - {get_text('dialogs.messages.continue_text')}"
        self.continue_btn = ModernButton(continue_text, "primary")
        parent.add_widget(self.continue_btn)
    
    def _connect_signals(self):
        """连接信号"""
        self.language_combo.currentTextChanged.connect(self._on_language_change)
        self.github_label.clicked.connect(self._open_github)
        self.continue_btn.clicked.connect(self._on_continue)
    
    def _on_language_change(self, selected_display: str):
        """处理语言变更"""
        available_langs = self.language_manager.get_available_languages()
        
        # 根据显示名称找到语言代码
        for code, display in available_langs.items():
            if display == selected_display:
                self.language_manager.set_language(code)
                self._update_texts()
                break
    
    def _update_texts(self):
        """更新所有文本"""
        self.title_label.setText(get_text("app.title"))
        self.welcome_title.setText(get_text("dialogs.titles.welcome_title"))
        self.lang_label.setText(get_text("app.language"))
        self.welcome_message.setText(get_text("dialogs.messages.welcome_message"))
        self.github_label.setText(get_text("copyright.github"))
        
        continue_text = f"{get_text('buttons.ok')} - {get_text('dialogs.messages.continue_text')}"
        self.continue_btn.setText(continue_text)
    
    def _open_github(self):
        """打开GitHub链接"""
        try:
            webbrowser.open(get_text("copyright.github"))
        except Exception as e:
            print(f"Error opening GitHub link: {e}")
    
    def _on_continue(self):
        """处理继续按钮点击"""
        # 标记首次运行完成
        self.config_manager.mark_first_run_complete()
        self.config_manager.set_show_welcome(False)
        
        # 发送继续信号
        self.continue_clicked.emit()
