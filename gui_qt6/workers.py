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
from augment_tools_core.database_manager import clean_ide_database, clean_ide_database_enhanced
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
        """执行清理数据库任务（增强版）"""
        try:
            self.emit_progress(f"开始清理 {self.ide_name} 数据库 (关键字: '{self.keyword}')")
            self.emit_status(f"正在清理 {self.ide_name} 数据库...", "info")

            # 使用增强版数据库清理，获取详细结果
            result = clean_ide_database_enhanced(self.ide_type, self.keyword)

            if self.is_cancelled:
                return

            if result["success"]:
                # 显示详细的清理结果
                if result["entries_removed"] > 0:
                    self.emit_progress(f"成功删除 {result['entries_removed']} 个包含关键字的条目")
                else:
                    self.emit_progress("未找到需要清理的条目")

                if result["backup_created"]:
                    self.emit_progress("已自动创建数据库备份")

                self.emit_progress("数据库清理过程完成。")
                self.emit_status("数据库清理完成", "success")
                self.task_completed.emit(True)
            else:
                error_msg = result.get("error_message", "未知错误")
                self.emit_progress(f"数据库清理失败: {error_msg}")
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


# === 新增工作线程：增强清理功能 ===

class EnhancedCleanupWorker(BaseWorker):
    """增强清理工作线程（支持多种清理模式）"""

    def __init__(self, ide_type: IDEType, mode: str = "hybrid",
                 keyword: str = "augment", force_delete: bool = False,
                 kill_processes: bool = False, parent=None):
        super().__init__(parent)
        self.ide_type = ide_type
        self.mode = mode
        self.keyword = keyword
        self.force_delete = force_delete
        self.kill_processes = kill_processes
        self.ide_name = get_ide_display_name(ide_type)

    def run(self):
        """执行增强清理任务"""
        import asyncio
        try:
            self.emit_progress(f"开始增强清理 {self.ide_name} (模式: {self.mode})")
            self.emit_status(f"正在执行增强清理...", "info")

            # 导入清理功能
            from augment_tools_core.database_manager import clean_ide_comprehensive

            # 执行异步清理
            async def run_cleanup():
                return await clean_ide_comprehensive(
                    ide_type=self.ide_type,
                    mode=self.mode,
                    keyword=self.keyword,
                    force_delete=self.force_delete,
                    kill_processes=self.kill_processes
                )

            # 在新的事件循环中运行
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            result = loop.run_until_complete(run_cleanup())

            if self.is_cancelled:
                return

            if result["success"]:
                # 显示详细结果
                self.emit_progress("清理结果:")
                if result.get("database_cleaned"):
                    self.emit_progress(f"  数据库清理: 删除 {result.get('database_entries_removed', 0)} 个条目")
                if result.get("files_deleted", 0) > 0:
                    self.emit_progress(f"  文件删除: {result['files_deleted']} 个文件")
                    self.emit_progress(f"    - globalStorage: {result.get('global_storage_files', 0)} 个")
                    self.emit_progress(f"    - workspaceStorage: {result.get('workspace_storage_files', 0)} 个")
                if result.get("processes_killed", 0) > 0:
                    self.emit_progress(f"  进程终止: {result['processes_killed']} 个进程")

                self.emit_progress("增强清理完成。")
                self.emit_status("增强清理完成", "success")
                self.task_completed.emit(True)
            else:
                error_messages = result.get("errors", ["未知错误"])
                for error in error_messages:
                    self.emit_progress(f"错误: {error}")
                self.emit_status("增强清理失败", "error")
                self.task_completed.emit(False)

        except Exception as e:
            self.emit_progress(f"增强清理时发生错误: {str(e)}")
            self.emit_status(f"清理失败: {str(e)}", "error")
            self.task_completed.emit(False)

class ProcessManagerWorker(BaseWorker):
    """进程管理工作线程"""

    def __init__(self, ide_type: IDEType, action: str = "check", parent=None):
        super().__init__(parent)
        self.ide_type = ide_type
        self.action = action  # "check" 或 "kill"
        self.ide_name = get_ide_display_name(ide_type)

    def run(self):
        """执行进程管理任务"""
        try:
            from augment_tools_core.process_manager import ProcessManager

            pm = ProcessManager()

            if self.action == "check":
                self.emit_progress(f"检查 {self.ide_name} 进程...")
                processes = pm.get_ide_processes(self.ide_type)

                if processes:
                    self.emit_progress(f"找到 {len(processes)} 个 {self.ide_name} 进程:")
                    for proc in processes:
                        self.emit_progress(f"  {proc}")
                    self.emit_status(f"找到 {len(processes)} 个进程", "info")
                else:
                    self.emit_progress(f"未找到 {self.ide_name} 进程")
                    self.emit_status("未找到进程", "info")

                self.task_completed.emit(True)

            elif self.action == "kill":
                self.emit_progress(f"终止 {self.ide_name} 进程...")

                import asyncio

                async def kill_processes():
                    return await pm.kill_ide_processes(self.ide_type, force=True)

                # 在新的事件循环中运行
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                success = loop.run_until_complete(kill_processes())

                if success:
                    self.emit_progress("所有进程已成功终止")
                    self.emit_status("进程终止完成", "success")
                    self.task_completed.emit(True)
                else:
                    self.emit_progress("部分进程可能无法终止")
                    self.emit_status("进程终止部分失败", "warning")
                    self.task_completed.emit(False)

        except Exception as e:
            self.emit_progress(f"进程管理时发生错误: {str(e)}")
            self.emit_status(f"操作失败: {str(e)}", "error")
            self.task_completed.emit(False)


# 导出所有工作线程
__all__ = [
    'BaseWorker',
    'CloseIDEWorker', 
    'CleanDatabaseWorker',
    'ModifyIDsWorker',
    'RunAllWorker'
]
