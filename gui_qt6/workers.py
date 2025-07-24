#!/usr/bin/env python3
"""
工作线程类
优化性能，避免UI线程阻塞
"""

import psutil
from PyQt6.QtCore import QThread, pyqtSignal
from augment_tools_core.common_utils import (
    IDEType, get_ide_display_name, get_ide_process_names
)
from augment_tools_core.database_manager import clean_ide_database
from augment_tools_core.telemetry_manager import modify_ide_telemetry_ids


class BaseWorker(QThread):
    """基础工作线程"""
    
    # 信号定义
    progress_updated = pyqtSignal(str)  # 进度更新
    status_changed = pyqtSignal(str, str)  # 状态变化 (message, type)
    task_completed = pyqtSignal(bool)  # 任务完成 (success)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_cancelled = False
    
    def cancel(self):
        """取消任务"""
        self.is_cancelled = True
    
    def emit_progress(self, message: str):
        """发送进度信息"""
        if not self.is_cancelled:
            self.progress_updated.emit(message)
    
    def emit_status(self, message: str, status_type: str = "info"):
        """发送状态信息"""
        if not self.is_cancelled:
            self.status_changed.emit(message, status_type)


class CloseIDEWorker(BaseWorker):
    """关闭IDE工作线程"""
    
    def __init__(self, ide_type: IDEType, parent=None):
        super().__init__(parent)
        self.ide_type = ide_type
        self.ide_name = get_ide_display_name(ide_type)
    
    def run(self):
        """执行关闭IDE任务"""
        try:
            self.emit_progress(f"正在关闭 {self.ide_name}...")
            self.emit_status(f"正在关闭 {self.ide_name}...", "info")
            
            # 获取进程名称
            process_names = get_ide_process_names(self.ide_type)
            closed_any = False
            
            # 查找并关闭进程
            for proc in psutil.process_iter(['pid', 'name']):
                if self.is_cancelled:
                    return
                
                if proc.info['name'] in process_names:
                    try:
                        proc.terminate()
                        closed_any = True
                        self.emit_progress(f"已关闭 {proc.info['name']} (PID: {proc.info['pid']})")
                    except Exception as e:
                        self.emit_progress(f"关闭进程失败: {e}")
                        self.emit_status(f"关闭进程失败: {e}", "error")
            
            if closed_any:
                self.emit_progress(f"{self.ide_name} 已成功关闭")
                self.emit_status(f"{self.ide_name} 已成功关闭", "success")
                self.task_completed.emit(True)
            else:
                self.emit_progress(f"未找到运行中的 {self.ide_name} 进程")
                self.emit_status(f"未找到运行中的 {self.ide_name} 进程", "warning")
                self.task_completed.emit(True)
                
        except Exception as e:
            self.emit_progress(f"关闭 {self.ide_name} 时发生错误: {str(e)}")
            self.emit_status(f"关闭失败: {str(e)}", "error")
            self.task_completed.emit(False)


class CleanDatabaseWorker(BaseWorker):
    """清理数据库工作线程"""
    
    def __init__(self, ide_type: IDEType, keyword: str, parent=None):
        super().__init__(parent)
        self.ide_type = ide_type
        self.keyword = keyword
        self.ide_name = get_ide_display_name(ide_type)
    
    def run(self):
        """执行清理数据库任务"""
        try:
            self.emit_progress(f"开始清理 {self.ide_name} 数据库 (关键字: '{self.keyword}')")
            self.emit_status(f"正在清理 {self.ide_name} 数据库...", "info")
            
            # 执行数据库清理
            success = clean_ide_database(self.ide_type, self.keyword)
            
            if self.is_cancelled:
                return
            
            if success:
                self.emit_progress("数据库清理过程完成。")
                self.emit_status("数据库清理完成", "success")
                self.task_completed.emit(True)
            else:
                self.emit_progress("数据库清理过程报告错误。请检查之前的消息。")
                self.emit_status("数据库清理失败", "error")
                self.task_completed.emit(False)
                
        except Exception as e:
            self.emit_progress(f"清理数据库时发生错误: {str(e)}")
            self.emit_status(f"清理失败: {str(e)}", "error")
            self.task_completed.emit(False)


class ModifyIDsWorker(BaseWorker):
    """修改遥测ID工作线程"""
    
    def __init__(self, ide_type: IDEType, parent=None):
        super().__init__(parent)
        self.ide_type = ide_type
        self.ide_name = get_ide_display_name(ide_type)
    
    def run(self):
        """执行修改遥测ID任务"""
        try:
            self.emit_progress(f"开始修改 {self.ide_name} 遥测 ID")
            self.emit_status(f"正在修改 {self.ide_name} 遥测ID...", "info")
            
            # 执行遥测ID修改
            success = modify_ide_telemetry_ids(self.ide_type)
            
            if self.is_cancelled:
                return
            
            if success:
                self.emit_progress("遥测 ID 修改过程完成。")
                self.emit_status("遥测ID修改完成", "success")
                self.task_completed.emit(True)
            else:
                self.emit_progress("遥测 ID 修改过程报告错误。请检查之前的消息。")
                self.emit_status("遥测ID修改失败", "error")
                self.task_completed.emit(False)
                
        except Exception as e:
            self.emit_progress(f"修改遥测 ID 时发生错误: {str(e)}")
            self.emit_status(f"修改失败: {str(e)}", "error")
            self.task_completed.emit(False)


class RunAllWorker(BaseWorker):
    """一键执行所有工具工作线程"""
    
    def __init__(self, ide_type: IDEType, keyword: str, parent=None):
        super().__init__(parent)
        self.ide_type = ide_type
        self.keyword = keyword
        self.ide_name = get_ide_display_name(ide_type)
    
    def run(self):
        """执行所有工具任务"""
        try:
            self.emit_progress(f"开始为 {self.ide_name} 执行所有工具")
            self.emit_status(f"正在执行一键修改...", "info")
            
            # 步骤1: 关闭IDE
            self.emit_progress(f"步骤 1: 关闭 {self.ide_name}")
            self._close_ide()
            
            if self.is_cancelled:
                return
            
            # 步骤2: 清理数据库
            self.emit_progress(f"步骤 2: 清理 {self.ide_name} 数据库")
            db_success = clean_ide_database(self.ide_type, self.keyword)
            
            if self.is_cancelled:
                return
            
            if db_success:
                self.emit_progress("数据库清理完成")
            else:
                self.emit_progress("数据库清理失败")
            
            # 步骤3: 修改遥测ID
            self.emit_progress(f"步骤 3: 修改 {self.ide_name} 遥测ID")
            id_success = modify_ide_telemetry_ids(self.ide_type)
            
            if self.is_cancelled:
                return
            
            if id_success:
                self.emit_progress("遥测ID修改完成")
            else:
                self.emit_progress("遥测ID修改失败")
            
            # 完成
            overall_success = db_success and id_success
            if overall_success:
                self.emit_progress(f"{self.ide_name}所有工具已完成执行序列。")
                self.emit_status("一键修改完成", "success")
            else:
                self.emit_progress(f"{self.ide_name}部分工具执行失败。")
                self.emit_status("一键修改部分失败", "warning")
            
            self.task_completed.emit(overall_success)
            
        except Exception as e:
            self.emit_progress(f"运行所有工具时发生错误: {str(e)}")
            self.emit_status(f"执行失败: {str(e)}", "error")
            self.task_completed.emit(False)
    
    def _close_ide(self):
        """关闭IDE的内部方法"""
        try:
            process_names = get_ide_process_names(self.ide_type)
            for proc in psutil.process_iter(['pid', 'name']):
                if self.is_cancelled:
                    return
                if proc.info['name'] in process_names:
                    try:
                        proc.terminate()
                        self.emit_progress(f"已关闭 {proc.info['name']} (PID: {proc.info['pid']})")
                    except Exception as e:
                        self.emit_progress(f"关闭进程失败: {e}")
        except Exception as e:
            self.emit_progress(f"关闭IDE时发生错误: {e}")


# 导出所有工作线程
__all__ = [
    'BaseWorker',
    'CloseIDEWorker', 
    'CleanDatabaseWorker',
    'ModifyIDsWorker',
    'RunAllWorker'
]
