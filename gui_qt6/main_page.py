#!/usr/bin/env python3
"""
PyQt6主功能页面
替代原有的Tkinter主页面
"""

import webbrowser
import psutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QTextEdit, QMessageBox, QSpacerItem, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QTextCursor

from .components import (
    TitleLabel, SubtitleLabel, SecondaryLabel, LinkLabel,
    ModernButton, StatusLabel, SectionFrame
)
from .workers import CloseIDEWorker, CleanDatabaseWorker, ModifyIDsWorker, RunAllWorker
from .font_manager import get_default_font, get_monospace_font
from augment_tools_core.common_utils import (
    IDEType, get_ide_display_name, get_ide_process_names
)
from language_manager import get_language_manager, get_text
from .about_dialog import AboutDialog


class MainPage(QWidget):
    """PyQt6主功能页面"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.language_manager = get_language_manager(config_manager)
        
        # 当前工作线程
        self.current_worker = None
        
        # 进程检查缓存
        self._process_cache = {}
        self._cache_timer = QTimer()
        self._cache_timer.timeout.connect(self._clear_process_cache)
        self._cache_timer.start(2000)  # 每2秒清理缓存
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """设置用户界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 15, 25, 15)  # 减少边距
        main_layout.setSpacing(15)  # 减少间距
        
        # 顶部栏
        self._create_top_bar(main_layout)
        
        # 标题区域
        self._create_title_section(main_layout)
        
        # IDE选择区域
        self._create_ide_section(main_layout)
        
        # 按钮区域
        self._create_buttons_section(main_layout)
        
        # 日志区域
        self._create_log_section(main_layout)
        
        # 状态显示
        self._create_status_section(main_layout)
        
        # 底部信息
        self._create_bottom_section(main_layout)
        
        # 添加弹性空间
        main_layout.addStretch()
    
    def _create_top_bar(self, parent_layout):
        """创建顶部栏"""
        top_layout = QHBoxLayout()
        
        # 语言选择
        lang_label = SecondaryLabel(get_text("app.language"))
        top_layout.addWidget(lang_label)
        
        self.language_combo = QComboBox()
        self.language_combo.setFont(get_default_font(9))
        self.language_combo.setMaximumWidth(120)
        
        # 填充语言选项
        available_langs = self.language_manager.get_available_languages()
        lang_values = list(available_langs.values())
        self.language_combo.addItems(lang_values)
        
        # 设置当前语言
        current_lang = self.language_manager.get_language()
        current_display = available_langs.get(current_lang, lang_values[0])
        current_index = lang_values.index(current_display) if current_display in lang_values else 0
        self.language_combo.setCurrentIndex(current_index)
        
        top_layout.addWidget(self.language_combo)
        top_layout.addStretch()
        
        # 关于按钮
        self.about_btn = ModernButton(get_text("app.about"), "secondary")
        # 根据语言调整按钮宽度
        if self.config_manager.get_language() == "en_US":
            self.about_btn.setMaximumWidth(100)  # 英文版本增加宽度
        else:
            self.about_btn.setMaximumWidth(80)   # 中文版本保持原宽度
        top_layout.addWidget(self.about_btn)
        
        parent_layout.addLayout(top_layout)
    
    def _create_title_section(self, parent_layout):
        """创建标题区域"""
        self.title_label = TitleLabel(get_text("app.title"), 18)
        parent_layout.addWidget(self.title_label)
        
        self.welcome_label = SecondaryLabel(get_text("app.welcome"))
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(self.welcome_label)
    
    def _create_ide_section(self, parent_layout):
        """创建IDE选择区域"""
        # IDE选择标签
        self.ide_label = SubtitleLabel(get_text("app.select_ide"))
        parent_layout.addWidget(self.ide_label)
        
        # IDE选择框架
        ide_frame = SectionFrame()
        ide_layout = QVBoxLayout(ide_frame)
        
        # IDE下拉框
        self.ide_combo = QComboBox()
        self.ide_combo.setFont(get_default_font(10))
        self.ide_combo.addItems(["VS Code", "Cursor", "Windsurf"])
        
        # 设置上次选择的IDE
        last_ide = self.config_manager.get_last_selected_ide()
        if last_ide in ["VS Code", "Cursor", "Windsurf"]:
            self.ide_combo.setCurrentText(last_ide)
        
        ide_layout.addWidget(self.ide_combo)
        parent_layout.addWidget(ide_frame)
    
    def _create_buttons_section(self, parent_layout):
        """创建按钮区域"""
        # 一键修改按钮
        self.run_all_btn = ModernButton(get_text("buttons.run_all"), "primary")
        parent_layout.addWidget(self.run_all_btn)
        
        # 关闭IDE按钮
        self.close_ide_btn = ModernButton(get_text("buttons.close_ide"), "warning")
        parent_layout.addWidget(self.close_ide_btn)
        
        # 清理数据库按钮
        self.clean_db_btn = ModernButton(get_text("buttons.clean_db"), "secondary")
        parent_layout.addWidget(self.clean_db_btn)
        
        # 修改遥测ID按钮
        self.modify_ids_btn = ModernButton(get_text("buttons.modify_ids"), "secondary")
        parent_layout.addWidget(self.modify_ids_btn)
    
    def _create_log_section(self, parent_layout):
        """创建日志区域"""
        log_label = SubtitleLabel("操作日志:")
        parent_layout.addWidget(log_label)

        # 创建日志容器
        log_container = QFrame()
        log_container.setMaximumHeight(100)  # 减少高度以节省垂直空间
        log_container.setStyleSheet("QFrame { border: 1px solid #e2e8f0; border-radius: 6px; }")

        # 日志文本框
        self.log_text = QTextEdit(log_container)
        self.log_text.setFont(get_monospace_font(9))
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("QTextEdit { border: none; background: transparent; }")

        # 清空日志按钮 - 放在右下角
        self.clear_log_btn = ModernButton(get_text("buttons.clear_log"), "secondary")
        self.clear_log_btn.setParent(log_container)
        # 根据语言调整按钮宽度
        if self.config_manager.get_language() == "en_US":
            btn_width = 120  # 英文版本增加宽度
        else:
            btn_width = 100  # 中文版本保持原宽度

        self.clear_log_btn.setFixedSize(btn_width, 25)

        # 重写容器的resizeEvent来定位按钮
        def resize_log_container(event):
            # 调整日志文本框大小
            self.log_text.setGeometry(5, 5, event.size().width() - 10, event.size().height() - 10)
            # 将按钮定位到右下角
            btn_x = event.size().width() - btn_width - 10
            btn_y = event.size().height() - 30
            self.clear_log_btn.move(btn_x, btn_y)
            self.clear_log_btn.raise_()  # 确保按钮在最上层

        log_container.resizeEvent = resize_log_container
        parent_layout.addWidget(log_container)
    
    def _create_status_section(self, parent_layout):
        """创建状态显示区域"""
        self.status_label = StatusLabel()
        parent_layout.addWidget(self.status_label)
    
    def _create_bottom_section(self, parent_layout):
        """创建底部信息区域"""
        # 版本信息
        self.version_label = SecondaryLabel(get_text("app.version"))
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(self.version_label)
        
        # 版权信息
        self.copyright_label = SecondaryLabel(get_text("copyright.notice"))
        self.copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(self.copyright_label)
        
        # GitHub链接
        github_layout = QHBoxLayout()
        github_layout.addStretch()
        
        open_source_label = SecondaryLabel(get_text("copyright.open_source"))
        github_layout.addWidget(open_source_label)
        
        self.github_link = LinkLabel("GitHub")
        github_layout.addWidget(self.github_link)
        
        github_layout.addStretch()
        parent_layout.addLayout(github_layout)
        
        # 防诈骗警告
        self.fraud_label = SecondaryLabel(get_text("copyright.report_fraud"))
        self.fraud_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fraud_label.setStyleSheet("color: #dc2626; font-weight: bold;")
        parent_layout.addWidget(self.fraud_label)
    
    def _connect_signals(self):
        """连接信号"""
        # 语言切换
        self.language_combo.currentTextChanged.connect(self._on_language_change)
        
        # IDE选择
        self.ide_combo.currentTextChanged.connect(self._on_ide_change)
        
        # 按钮点击
        self.about_btn.clicked.connect(self._show_about)
        self.run_all_btn.clicked.connect(self._run_all_clicked)
        self.close_ide_btn.clicked.connect(self._close_ide_clicked)
        self.clean_db_btn.clicked.connect(self._clean_database_clicked)
        self.modify_ids_btn.clicked.connect(self._modify_ids_clicked)
        self.clear_log_btn.clicked.connect(self._clear_log)
        
        # GitHub链接
        self.github_link.clicked.connect(self._open_github)

    def _clear_process_cache(self):
        """清理进程缓存"""
        self._process_cache.clear()

    def _on_language_change(self, selected_display: str):
        """处理语言变更"""
        available_langs = self.language_manager.get_available_languages()

        for code, display in available_langs.items():
            if display == selected_display:
                self.language_manager.set_language(code)
                self._update_ui_texts()
                break

    def _on_ide_change(self, selected_ide: str):
        """处理IDE选择变更"""
        self.config_manager.set_last_selected_ide(selected_ide)

    def _update_ui_texts(self):
        """更新所有UI文本"""
        # 更新按钮文本
        self.run_all_btn.setText(get_text("buttons.run_all"))
        self.close_ide_btn.setText(get_text("buttons.close_ide"))
        self.clean_db_btn.setText(get_text("buttons.clean_db"))
        self.modify_ids_btn.setText(get_text("buttons.modify_ids"))
        self.clear_log_btn.setText(get_text("buttons.clear_log"))
        self.about_btn.setText(get_text("app.about"))

        # 根据语言调整按钮宽度
        if self.config_manager.get_language() == "en_US":
            self.about_btn.setMaximumWidth(100)
            # 清理日志按钮现在在日志框内，需要重新设置大小
            btn_width = 120
            self.clear_log_btn.setFixedSize(btn_width, 25)
        else:
            self.about_btn.setMaximumWidth(80)
            # 清理日志按钮现在在日志框内，需要重新设置大小
            btn_width = 100
            self.clear_log_btn.setFixedSize(btn_width, 25)

        # 更新标签文本
        self.title_label.setText(get_text("app.title"))
        self.welcome_label.setText(get_text("app.welcome"))
        self.ide_label.setText(get_text("app.select_ide"))
        self.version_label.setText(get_text("app.version"))
        self.copyright_label.setText(get_text("copyright.notice"))
        self.fraud_label.setText(get_text("copyright.report_fraud"))

    def _show_about(self):
        """显示关于对话框"""
        AboutDialog(self, self.config_manager, show_dont_show_again=True).show()

    def _open_github(self):
        """打开GitHub链接"""
        try:
            webbrowser.open(get_text("copyright.github"))
        except Exception as e:
            print(f"Error opening GitHub link: {e}")

    def _clear_log(self):
        """清空日志"""
        self.log_text.clear()

    def _add_log(self, message: str):
        """添加日志信息"""
        self.log_text.append(message)
        # 滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def get_selected_ide_type(self) -> IDEType:
        """获取选中的IDE类型"""
        ide_name = self.ide_combo.currentText()
        if ide_name == "VS Code":
            return IDEType.VSCODE
        elif ide_name == "Cursor":
            return IDEType.CURSOR
        elif ide_name == "Windsurf":
            return IDEType.WINDSURF
        else:
            return IDEType.VSCODE  # 默认

    def _is_ide_running(self, ide_type: IDEType) -> bool:
        """检查IDE是否正在运行"""
        cache_key = f"ide_running_{ide_type.value}"

        # 检查缓存
        if cache_key in self._process_cache:
            return self._process_cache[cache_key]

        try:
            process_names = get_ide_process_names(ide_type)
            is_running = False

            for proc in psutil.process_iter(['name']):
                if proc.info['name'] in process_names:
                    is_running = True
                    break

            # 缓存结果
            self._process_cache[cache_key] = is_running
            return is_running

        except Exception:
            self._process_cache[cache_key] = False
            return False

    def _set_buttons_enabled(self, enabled: bool):
        """设置所有按钮的启用状态"""
        self.run_all_btn.set_enabled_state(enabled)
        self.close_ide_btn.set_enabled_state(enabled)
        self.clean_db_btn.set_enabled_state(enabled)
        self.modify_ids_btn.set_enabled_state(enabled)

    def _show_warning_dialog(self, title: str, message: str) -> bool:
        """显示警告对话框"""
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def _show_info_dialog(self, title: str, message: str):
        """显示信息对话框"""
        QMessageBox.information(self, title, message)

    def _run_all_clicked(self):
        """处理一键修改按钮点击"""
        ide_type = self.get_selected_ide_type()
        ide_name = get_ide_display_name(ide_type)

        # 显示确认对话框
        if not self._show_warning_dialog(
            get_text("dialogs.titles.run_all_confirm"),
            get_text("dialogs.messages.run_all_warning", ide_name=ide_name)
        ):
            return

        # 禁用按钮
        self._set_buttons_enabled(False)

        # 创建并启动工作线程
        self.current_worker = RunAllWorker(ide_type, "augment")
        self._connect_worker_signals(self.current_worker)
        self.current_worker.start()

    def _close_ide_clicked(self):
        """处理关闭IDE按钮点击"""
        ide_type = self.get_selected_ide_type()
        ide_name = get_ide_display_name(ide_type)

        # 显示确认对话框
        if not self._show_warning_dialog(
            get_text("dialogs.titles.close_confirm", ide_name=ide_name),
            get_text("dialogs.messages.close_warning", ide_name=ide_name)
        ):
            return

        # 禁用按钮
        self._set_buttons_enabled(False)

        # 创建并启动工作线程
        self.current_worker = CloseIDEWorker(ide_type)
        self._connect_worker_signals(self.current_worker)
        self.current_worker.start()

    def _clean_database_clicked(self):
        """处理清理数据库按钮点击"""
        ide_type = self.get_selected_ide_type()
        ide_name = get_ide_display_name(ide_type)

        # 检查IDE是否正在运行
        if self._is_ide_running(ide_type):
            self._show_info_dialog(
                get_text("dialogs.titles.ide_running", ide_name=ide_name),
                get_text("dialogs.messages.ide_running_warning", ide_name=ide_name)
            )
            return

        # 禁用按钮
        self._set_buttons_enabled(False)

        # 创建并启动工作线程
        self.current_worker = CleanDatabaseWorker(ide_type, "augment")
        self._connect_worker_signals(self.current_worker)
        self.current_worker.start()

    def _modify_ids_clicked(self):
        """处理修改遥测ID按钮点击"""
        ide_type = self.get_selected_ide_type()
        ide_name = get_ide_display_name(ide_type)

        # 检查IDE是否正在运行
        if self._is_ide_running(ide_type):
            self._show_info_dialog(
                get_text("dialogs.titles.ide_running", ide_name=ide_name),
                get_text("dialogs.messages.ide_running_warning", ide_name=ide_name)
            )
            return

        # 禁用按钮
        self._set_buttons_enabled(False)

        # 创建并启动工作线程
        self.current_worker = ModifyIDsWorker(ide_type)
        self._connect_worker_signals(self.current_worker)
        self.current_worker.start()

    def _connect_worker_signals(self, worker):
        """连接工作线程信号"""
        worker.progress_updated.connect(self._add_log)
        worker.status_changed.connect(self.status_label.show_status)
        worker.task_completed.connect(self._on_task_completed)

    def _on_task_completed(self, success: bool):
        """处理任务完成"""
        # 重新启用按钮
        self._set_buttons_enabled(True)

        # 清理工作线程
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None

        # 显示完成状态
        if success:
            self.status_label.show_status(get_text("status.success"), "success")
        else:
            self.status_label.show_status(get_text("status.error"), "error")

        # 3秒后隐藏状态
        QTimer.singleShot(3000, self.status_label.hide_status)
