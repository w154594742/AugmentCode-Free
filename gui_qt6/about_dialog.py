#!/usr/bin/env python3
"""
PyQt6关于对话框
替代原有的Tkinter关于对话框
"""

import webbrowser
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QCheckBox, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .font_manager import get_default_font, get_title_font
from language_manager import get_text


class AboutDialog(QDialog):
    """PyQt6关于对话框"""
    
    def __init__(self, parent=None, config_manager=None, show_dont_show_again=False):
        super().__init__(parent)
        self.config_manager = config_manager
        self.show_dont_show_again = show_dont_show_again
        
        self._setup_dialog()
        self._setup_ui()
        self._connect_signals()

        # 强制刷新布局，确保所有组件正确显示
        self.adjustSize()
        self.updateGeometry()
        self.update()
    
    def _setup_dialog(self):
        """设置对话框属性"""
        self.setWindowTitle(get_text("dialogs.titles.about_title"))
        self.setModal(True)
        self.setFixedSize(520, 650)  # 进一步增加宽度和高度

        # 居中显示
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def _setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)  # 增加边距
        layout.setSpacing(18)  # 增加间距
        
        # 标题
        title_label = QLabel(get_text("app.title"))
        title_label.setFont(get_title_font(18))  # 稍微减小字体
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #4f46e5; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(title_label)

        # 版本信息
        version_label = QLabel(get_text("app.version"))
        version_label.setFont(get_default_font(11))  # 稍微减小字体
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #6b7280; margin-bottom: 10px;")
        layout.addWidget(version_label)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #e5e7eb;")
        layout.addWidget(line)
        
        # 描述信息
        desc_text = "AugmentCode-Free 是一个开源免费的IDE维护工具。"
        desc_label = QLabel(desc_text)
        desc_label.setFont(get_default_font(10))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #374151; margin: 8px 0px;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        # 创建并列布局：支持的IDE和主要功能
        features_layout = QHBoxLayout()
        features_layout.setSpacing(20)

        # 左侧：支持的IDE
        ide_frame = QFrame()
        ide_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        ide_layout = QVBoxLayout(ide_frame)
        ide_layout.setSpacing(8)

        ide_title = QLabel("支持的IDE:")
        ide_title.setFont(get_default_font(10, bold=True))
        ide_title.setStyleSheet("color: #374151 !important; margin-bottom: 5px; background: transparent;")
        ide_layout.addWidget(ide_title)

        ide_list = QLabel("• VS Code\n• Cursor\n• Windsurf")
        ide_list.setFont(get_default_font(9))
        ide_list.setStyleSheet("color: #4b5563 !important; line-height: 1.5; background: transparent;")
        ide_layout.addWidget(ide_list)

        # 右侧：主要功能
        func_frame = QFrame()
        func_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        func_layout = QVBoxLayout(func_frame)
        func_layout.setSpacing(8)

        func_title = QLabel("主要功能:")
        func_title.setFont(get_default_font(10, bold=True))
        func_title.setStyleSheet("color: #374151 !important; margin-bottom: 5px; background: transparent;")
        func_layout.addWidget(func_title)

        func_list = QLabel("• 清理IDE数据库\n• 修改遥测ID\n• 一键修改所有配置")
        func_list.setFont(get_default_font(9))
        func_list.setStyleSheet("color: #4b5563 !important; line-height: 1.5; background: transparent;")
        func_layout.addWidget(func_list)

        # 添加到并列布局
        features_layout.addWidget(ide_frame)
        features_layout.addWidget(func_frame)
        layout.addLayout(features_layout)

        # 添加开源声明
        opensource_label = QLabel("本项目完全开源免费！")
        opensource_label.setFont(get_default_font(10, bold=True))
        opensource_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        opensource_label.setStyleSheet("color: #059669; margin: 10px 0px;")
        layout.addWidget(opensource_label)
        
        # 警告信息
        warning_frame = QFrame()
        warning_frame.setStyleSheet("""
            QFrame {
                background-color: #fef3c7;
                border: 1px solid #f59e0b;
                border-radius: 6px;
                padding: 8px;
                margin: 5px 0px;
            }
        """)
        warning_layout = QVBoxLayout(warning_frame)
        warning_layout.setContentsMargins(8, 8, 8, 8)  # 减小内边距

        warning_text = "⚠️ 重要提示：\n本项目完全开源免费！如果有人向您收费，请立即联系销售方退款并举报诈骗行为。"
        warning_label = QLabel(warning_text)
        warning_label.setFont(get_default_font(8))  # 减小字体
        warning_label.setStyleSheet("color: #92400e; line-height: 1.3;")
        warning_label.setWordWrap(True)
        warning_layout.addWidget(warning_label)

        layout.addWidget(warning_frame)
        
        # GitHub链接
        github_layout = QHBoxLayout()
        github_layout.addStretch()

        github_label = QLabel("项目地址：")
        github_label.setFont(get_default_font(9))  # 减小字体
        github_label.setStyleSheet("color: #6b7280; margin: 5px 0px;")
        github_layout.addWidget(github_label)

        self.github_link = QLabel("GitHub")
        self.github_link.setFont(get_default_font(9))  # 减小字体
        self.github_link.setStyleSheet("""
            color: #3b82f6;
            text-decoration: underline;
            margin: 5px 0px;
        """)
        self.github_link.setCursor(Qt.CursorShape.PointingHandCursor)
        github_layout.addWidget(self.github_link)

        github_layout.addStretch()
        layout.addLayout(github_layout)
        
        # 适量弹性空间
        layout.addSpacing(10)  # 使用固定间距替代弹性空间

        # 底部按钮区域
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(10)  # 设置间距

        # "启动时不再显示"选项
        if self.show_dont_show_again:
            self.dont_show_checkbox = QCheckBox("启动时不再显示此对话框")
            self.dont_show_checkbox.setFont(get_default_font(8))  # 减小字体
            self.dont_show_checkbox.setStyleSheet("color: #6b7280; margin: 5px 0px;")
            bottom_layout.addWidget(self.dont_show_checkbox)
        
        # 确定按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton(get_text("buttons.ok"))
        self.ok_button.setFont(get_default_font(9, bold=True))  # 减小字体
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4f46e5;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 20px;
                min-width: 70px;
                margin: 5px 0px;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
            QPushButton:pressed {
                background-color: #3730a3;
            }
        """)
        self.ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.ok_button)

        button_layout.addStretch()
        bottom_layout.addLayout(button_layout)

        layout.addLayout(bottom_layout)

        # 强制刷新所有组件，确保文字正确显示
        self.layout().update()
        for child in self.findChildren(QLabel):
            child.adjustSize()
            child.update()
        for child in self.findChildren(QFrame):
            child.update()
    
    def _connect_signals(self):
        """连接信号"""
        self.github_link.mousePressEvent = self._open_github
        self.ok_button.clicked.connect(self._on_ok_clicked)
    
    def _open_github(self, event):
        """打开GitHub链接"""
        try:
            webbrowser.open(get_text("copyright.github"))
        except Exception as e:
            print(f"Error opening GitHub link: {e}")
    
    def _on_ok_clicked(self):
        """处理确定按钮点击"""
        # 保存"不再显示"设置
        if self.show_dont_show_again and hasattr(self, 'dont_show_checkbox'):
            if self.dont_show_checkbox.isChecked():
                if self.config_manager:
                    self.config_manager.set_show_about_on_startup(False)
        
        self.accept()
    
    def show(self):
        """显示对话框"""
        # 强制刷新布局和重绘
        self.updateGeometry()
        self.update()
        self.repaint()

        # 确保所有子组件也更新
        for child in self.findChildren(QLabel):
            child.updateGeometry()
            child.update()
            child.repaint()

        return self.exec()
