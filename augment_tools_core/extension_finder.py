#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩展文件查找器
自动查找不同IDE的AugmentCode扩展文件，支持多版本和便携版
"""

import os
import glob
from pathlib import Path
from typing import List, Dict, Optional
import platform

from .common_utils import IDEType, print_info, print_warning, print_error


class ExtensionFinder:
    """扩展文件查找器"""
    
    def __init__(self):
        self.system = platform.system().lower()
        
        # 扩展文件路径模式
        self.extension_patterns = {
            IDEType.VSCODE: {
                "windows": [
                    os.path.expanduser("~/.vscode/extensions/augment.vscode-augment-*/out/extension.js"),
                    os.path.expanduser("~/AppData/Roaming/Code/User/extensions/augment.vscode-augment-*/out/extension.js"),
                ],
                "linux": [
                    os.path.expanduser("~/.vscode/extensions/augment.vscode-augment-*/out/extension.js"),
                    os.path.expanduser("~/.config/Code/User/extensions/augment.vscode-augment-*/out/extension.js"),
                ],
                "darwin": [
                    os.path.expanduser("~/.vscode/extensions/augment.vscode-augment-*/out/extension.js"),
                    os.path.expanduser("~/Library/Application Support/Code/User/extensions/augment.vscode-augment-*/out/extension.js"),
                ]
            },
            IDEType.CURSOR: {
                "windows": [
                    os.path.expanduser("~/.cursor/extensions/augment.cursor-augment-*/out/extension.js"),
                    os.path.expanduser("~/AppData/Roaming/Cursor/User/extensions/augment.cursor-augment-*/out/extension.js"),
                ],
                "linux": [
                    os.path.expanduser("~/.cursor/extensions/augment.cursor-augment-*/out/extension.js"),
                    os.path.expanduser("~/.config/Cursor/User/extensions/augment.cursor-augment-*/out/extension.js"),
                ],
                "darwin": [
                    os.path.expanduser("~/.cursor/extensions/augment.cursor-augment-*/out/extension.js"),
                    os.path.expanduser("~/Library/Application Support/Cursor/User/extensions/augment.cursor-augment-*/out/extension.js"),
                ]
            },
            IDEType.WINDSURF: {
                "windows": [
                    os.path.expanduser("~/.windsurf/extensions/augment.windsurf-augment-*/out/extension.js"),
                    os.path.expanduser("~/AppData/Roaming/Windsurf/User/extensions/augment.windsurf-augment-*/out/extension.js"),
                ],
                "linux": [
                    os.path.expanduser("~/.windsurf/extensions/augment.windsurf-augment-*/out/extension.js"),
                    os.path.expanduser("~/.config/Windsurf/User/extensions/augment.windsurf-augment-*/out/extension.js"),
                ],
                "darwin": [
                    os.path.expanduser("~/.windsurf/extensions/augment.windsurf-augment-*/out/extension.js"),
                    os.path.expanduser("~/Library/Application Support/Windsurf/User/extensions/augment.windsurf-augment-*/out/extension.js"),
                ]
            }
        }
        
        # 通用扩展名模式（用于模糊匹配）
        self.generic_patterns = [
            "*augment*extension.js",
            "*augment*/out/extension.js", 
            "*augment*/dist/extension.js",
            "*augment*/build/extension.js"
        ]
    
    def find_extension_files(self, ide_type: IDEType, portable_root: Optional[str] = None) -> List[str]:
        """查找指定IDE的扩展文件"""
        found_files = []
        
        # 如果指定了便携版根目录
        if portable_root:
            portable_files = self._find_portable_extensions(ide_type, portable_root)
            found_files.extend(portable_files)
        
        # 查找标准安装位置
        standard_files = self._find_standard_extensions(ide_type)
        found_files.extend(standard_files)
        
        # 去重并验证文件
        unique_files = list(set(found_files))
        valid_files = [f for f in unique_files if os.path.exists(f) and self._is_valid_extension_file(f)]
        
        if valid_files:
            print_info(f"找到 {len(valid_files)} 个 {ide_type.value} 扩展文件:")
            for file in valid_files:
                print_info(f"  - {file}")
        else:
            print_warning(f"未找到 {ide_type.value} 的扩展文件")
        
        return valid_files
    
    def _find_standard_extensions(self, ide_type: IDEType) -> List[str]:
        """查找标准安装位置的扩展文件"""
        found_files = []
        
        if ide_type not in self.extension_patterns:
            print_warning(f"不支持的IDE类型: {ide_type}")
            return found_files
        
        patterns = self.extension_patterns[ide_type].get(self.system, [])
        
        for pattern in patterns:
            try:
                matches = glob.glob(pattern)
                found_files.extend(matches)
            except Exception as e:
                print_warning(f"搜索模式失败 {pattern}: {e}")
        
        return found_files
    
    def _find_portable_extensions(self, ide_type: IDEType, portable_root: str) -> List[str]:
        """查找便携版扩展文件"""
        found_files = []
        
        try:
            portable_path = Path(portable_root)
            if not portable_path.exists():
                print_warning(f"便携版路径不存在: {portable_root}")
                return found_files
            
            # 在便携版目录中搜索扩展文件
            search_patterns = [
                "extensions/augment*/out/extension.js",
                "data/extensions/augment*/out/extension.js",
                "user-data/extensions/augment*/out/extension.js",
                "resources/app/extensions/augment*/out/extension.js"
            ]
            
            for pattern in search_patterns:
                search_path = portable_path / pattern
                matches = glob.glob(str(search_path))
                found_files.extend(matches)
            
            # 递归搜索（限制深度）
            for root, dirs, files in os.walk(portable_root):
                # 限制搜索深度
                level = root.replace(portable_root, '').count(os.sep)
                if level >= 4:
                    dirs[:] = []  # 不再深入
                    continue
                
                for file in files:
                    if file == "extension.js" and "augment" in root.lower():
                        full_path = os.path.join(root, file)
                        found_files.append(full_path)
        
        except Exception as e:
            print_error(f"搜索便携版扩展失败: {e}")
        
        return found_files
    
    def _is_valid_extension_file(self, file_path: str) -> bool:
        """验证是否为有效的扩展文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # 只读取前1000字符
                
            # 检查是否包含关键标识
            indicators = [
                "callApi",
                "augment",
                "extension",
                "vscode",
                "activate"
            ]
            
            return any(indicator in content.lower() for indicator in indicators)
            
        except Exception:
            return False
    
    def find_all_extensions(self, portable_roots: Optional[Dict[IDEType, str]] = None) -> Dict[IDEType, List[str]]:
        """查找所有支持的IDE的扩展文件"""
        results = {}
        
        for ide_type in [IDEType.VSCODE, IDEType.CURSOR, IDEType.WINDSURF]:
            portable_root = None
            if portable_roots and ide_type in portable_roots:
                portable_root = portable_roots[ide_type]
            
            files = self.find_extension_files(ide_type, portable_root)
            if files:
                results[ide_type] = files
        
        return results
    
    def get_latest_extension(self, ide_type: IDEType, portable_root: Optional[str] = None) -> Optional[str]:
        """获取最新版本的扩展文件"""
        files = self.find_extension_files(ide_type, portable_root)
        
        if not files:
            return None
        
        # 按修改时间排序，返回最新的
        try:
            latest_file = max(files, key=lambda f: os.path.getmtime(f))
            return latest_file
        except Exception:
            # 如果获取修改时间失败，返回第一个
            return files[0]
    
    def search_by_keyword(self, keyword: str = "augment", search_paths: Optional[List[str]] = None) -> List[str]:
        """通过关键词搜索扩展文件"""
        found_files = []
        
        if not search_paths:
            # 默认搜索路径
            search_paths = [
                os.path.expanduser("~/.vscode"),
                os.path.expanduser("~/.cursor"), 
                os.path.expanduser("~/.windsurf"),
                os.path.expanduser("~/AppData/Roaming") if self.system == "windows" else "",
                os.path.expanduser("~/.config") if self.system == "linux" else "",
                os.path.expanduser("~/Library/Application Support") if self.system == "darwin" else ""
            ]
            search_paths = [p for p in search_paths if p and os.path.exists(p)]
        
        for search_path in search_paths:
            try:
                for root, dirs, files in os.walk(search_path):
                    # 限制搜索深度
                    level = root.replace(search_path, '').count(os.sep)
                    if level >= 5:
                        dirs[:] = []
                        continue
                    
                    if keyword.lower() in root.lower():
                        for file in files:
                            if file == "extension.js":
                                full_path = os.path.join(root, file)
                                if self._is_valid_extension_file(full_path):
                                    found_files.append(full_path)
            
            except Exception as e:
                print_warning(f"搜索路径失败 {search_path}: {e}")
        
        return list(set(found_files))  # 去重
