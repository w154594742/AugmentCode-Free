#!/usr/bin/env python3
"""
跨平台字体管理器 for PyQt6
解决macOS字体显示异常问题
"""

import platform
from typing import Dict, List, Optional
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication


class FontManager:
    """跨平台字体管理器"""
    
    def __init__(self):
        self.system = platform.system().lower()
        # PyQt6中QFontDatabase不需要参数
        self._font_database = QFontDatabase
        
        # 系统字体映射 - 解决macOS字体显示异常
        self.system_fonts = {
            'windows': {
                'default': ['Microsoft YaHei', 'SimHei', 'Arial', 'Segoe UI'],
                'monospace': ['Consolas', 'Courier New', 'monospace']
            },
            'darwin': {  # macOS
                'default': ['PingFang SC', 'Helvetica Neue', 'SF Pro Display', 'Arial'],
                'monospace': ['SF Mono', 'Monaco', 'Menlo', 'monospace']
            },
            'linux': {
                'default': ['Noto Sans CJK SC', 'DejaVu Sans', 'Ubuntu', 'Arial'],
                'monospace': ['Ubuntu Mono', 'DejaVu Sans Mono', 'monospace']
            }
        }
        
        # 缓存选中的字体
        self._default_font = None
        self._monospace_font = None
        
        # 初始化字体
        self._initialize_fonts()
    
    def _initialize_fonts(self):
        """初始化系统字体"""
        self._default_font = self._get_best_font('default')
        self._monospace_font = self._get_best_font('monospace')
    
    def _get_best_font(self, font_type: str) -> str:
        """获取最佳可用字体"""
        font_list = self.system_fonts.get(self.system, {}).get(font_type, ['Arial'])
        
        for font_name in font_list:
            if self._is_font_available(font_name):
                return font_name
        
        # 如果都不可用，返回系统默认
        return 'Arial' if font_type == 'default' else 'monospace'
    
    def _is_font_available(self, font_name: str) -> bool:
        """检查字体是否可用"""
        try:
            # PyQt6中QFontDatabase.families()是静态方法
            families = QFontDatabase.families()
            return font_name in families
        except:
            return False
    
    def get_default_font(self, size: int = 10, bold: bool = False) -> QFont:
        """获取默认字体"""
        font = QFont(self._default_font, size)
        font.setBold(bold)
        return font
    
    def get_monospace_font(self, size: int = 9) -> QFont:
        """获取等宽字体"""
        font = QFont(self._monospace_font, size)
        return font
    
    def get_title_font(self, size: int = 16) -> QFont:
        """获取标题字体"""
        font = QFont(self._default_font, size)
        font.setBold(True)
        return font
    
    def get_button_font(self, size: int = 10) -> QFont:
        """获取按钮字体"""
        font = QFont(self._default_font, size)
        font.setBold(True)
        return font
    
    def get_system_info(self) -> Dict:
        """获取系统字体信息"""
        return {
            'system': self.system,
            'platform': platform.platform(),
            'available_fonts_count': len(QFontDatabase.families()),
            'selected_default': self._default_font,
            'selected_monospace': self._monospace_font
        }


# 全局字体管理器实例
_font_manager = None


def get_font_manager() -> FontManager:
    """获取全局字体管理器实例"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager


def get_default_font(size: int = 10, bold: bool = False) -> QFont:
    """快捷方式：获取默认字体"""
    return get_font_manager().get_default_font(size, bold)


def get_monospace_font(size: int = 9) -> QFont:
    """快捷方式：获取等宽字体"""
    return get_font_manager().get_monospace_font(size)


def get_title_font(size: int = 16) -> QFont:
    """快捷方式：获取标题字体"""
    return get_font_manager().get_title_font(size)


def get_button_font(size: int = 10) -> QFont:
    """快捷方式：获取按钮字体"""
    return get_font_manager().get_button_font(size)


if __name__ == "__main__":
    # 测试字体管理器
    app = QApplication([])
    
    print("PyQt6 Font Manager Test")
    print("=" * 50)
    
    fm = get_font_manager()
    info = fm.get_system_info()
    
    print(f"System Info: {info}")
    print(f"Default Font: {fm._default_font} - {get_default_font().pointSize()}pt")
    print(f"Bold Font: {fm._default_font} - {get_title_font().pointSize()}pt - Bold: {get_title_font().bold()}")
    print(f"Monospace Font: {fm._monospace_font} - {get_monospace_font().pointSize()}pt")
    
    print("✅ PyQt6 Font manager test completed successfully!")
