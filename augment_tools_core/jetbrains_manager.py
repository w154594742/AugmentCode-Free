"""
JetBrains SessionID 管理器
用于修改 JetBrains 系列产品的 SessionID 配置
"""

import os
import platform
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional
from .common_utils import print_info, print_success, print_error, print_warning, create_backup


def get_jetbrains_products() -> List[str]:
    """
    获取支持的 JetBrains 产品列表
    
    Returns:
        支持的产品名称列表
    """
    return [
        "PyCharm",
        "IntelliJIdea", 
        "WebStorm",
        "PhpStorm",
        "CLion",
        "DataGrip",
        "GoLand",
        "RubyMine",
        "AppCode",
        "AndroidStudio",
        "Rider",
        "DataSpell"
    ]


def get_jetbrains_config_base() -> Optional[Path]:
    """
    获取 JetBrains 配置基础目录
    
    Returns:
        配置基础目录路径，如果不存在则返回 None
    """
    system = platform.system()
    
    if system == "Windows":
        # Windows: %APPDATA%\JetBrains
        appdata = os.environ.get("APPDATA")
        if appdata:
            config_base = Path(appdata) / "JetBrains"
        else:
            return None
    elif system == "Darwin":  # macOS
        # macOS: ~/Library/Application Support/JetBrains
        config_base = Path.home() / "Library" / "Application Support" / "JetBrains"
    else:  # Linux
        # Linux: ~/.config/JetBrains
        config_base = Path.home() / ".config" / "JetBrains"
    
    return config_base if config_base.exists() else None


def find_jetbrains_installations() -> Dict[str, List[Path]]:
    """
    查找已安装的 JetBrains 产品
    
    Returns:
        产品名称到配置目录列表的映射
    """
    config_base = get_jetbrains_config_base()
    if not config_base:
        return {}
    
    installations = {}
    products = get_jetbrains_products()
    
    print_info(f"检查 JetBrains 配置目录: {config_base}")
    
    try:
        for item in config_base.iterdir():
            if not item.is_dir():
                continue
                
            dir_name = item.name
            
            # 检查是否匹配任何已知产品
            for product in products:
                if dir_name.startswith(product):
                    if product not in installations:
                        installations[product] = []
                    installations[product].append(item)
                    print_info(f"找到 {product}: {dir_name}")
                    
    except PermissionError:
        print_error(f"无法访问 JetBrains 配置目录: {config_base}")
        return {}
    
    return installations


def generate_session_id() -> str:
    """
    生成新的 SessionID
    
    Returns:
        新的 UUID 字符串
    """
    return str(uuid.uuid4())


def modify_jetbrains_session_id(config_dir: Path, session_id: str) -> bool:
    """
    修改指定 JetBrains 产品配置目录中的 SessionID
    
    Args:
        config_dir: JetBrains 产品配置目录
        session_id: 新的 SessionID
        
    Returns:
        修改是否成功
    """
    options_dir = config_dir / "options"
    ide_general_file = options_dir / "ide.general.xml"
    
    # 检查字体配置文件，如果存在则跳过以保护用户设置
    font_config_file = options_dir / "font.options.xml"
    if font_config_file.exists():
        print_warning(f"检测到字体配置文件，跳过 {config_dir.name} 以保护用户设置")
        return True
    
    # 确保 options 目录存在
    options_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 如果配置文件存在，先备份
        if ide_general_file.exists():
            backup_path = create_backup(ide_general_file)
            if not backup_path:
                print_error(f"无法备份配置文件: {ide_general_file}")
                return False
            print_info(f"已备份配置文件: {backup_path}")
            
            # 读取现有配置
            tree = ET.parse(ide_general_file)
            root = tree.getroot()
        else:
            # 创建新的配置文件结构
            print_info(f"创建新配置文件: {ide_general_file}")
            root = ET.Element("application")
            component = ET.SubElement(root, "component", name="GeneralSettings")
            tree = ET.ElementTree(root)
        
        # 查找或创建 component
        component = root.find(".//component[@name='GeneralSettings']")
        if component is None:
            component = ET.SubElement(root, "component", name="GeneralSettings")
        
        # 查找现有的 augment.session.id 属性
        session_property = component.find(".//property[@name='augment.session.id']")
        
        if session_property is not None:
            # 更新现有属性
            old_session_id = session_property.get("value", "")
            if old_session_id:
                print_info(f"旧 SessionID: {old_session_id}")
            session_property.set("value", session_id)
        else:
            # 创建新属性
            session_property = ET.SubElement(component, "property", 
                                           name="augment.session.id", 
                                           value=session_id)
        
        # 保存文件
        tree.write(ide_general_file, encoding="utf-8", xml_declaration=True)
        print_success(f"✅ 已更新 SessionID: {session_id}")
        return True
        
    except Exception as e:
        print_error(f"修改 SessionID 失败: {e}")
        return False


def modify_all_jetbrains_session_ids(custom_session_id: Optional[str] = None) -> bool:
    """
    修改所有已安装 JetBrains 产品的 SessionID
    
    Args:
        custom_session_id: 自定义 SessionID，如果为 None 则自动生成
        
    Returns:
        是否至少有一个产品修改成功
    """
    if custom_session_id is None:
        custom_session_id = generate_session_id()
        print_info(f"生成的 SessionID: {custom_session_id}")
    else:
        print_info(f"使用自定义 SessionID: {custom_session_id}")
    
    installations = find_jetbrains_installations()
    
    if not installations:
        print_warning("未找到任何 JetBrains 产品安装")
        return False
    
    success_count = 0
    total_count = 0
    
    for product, config_dirs in installations.items():
        print_info(f"\n处理 {product}:")
        
        for config_dir in config_dirs:
            total_count += 1
            print_info(f"  处理版本: {config_dir.name}")
            
            if modify_jetbrains_session_id(config_dir, custom_session_id):
                success_count += 1
            else:
                print_error(f"  处理失败: {config_dir.name}")
    
    print_info(f"\n处理完成: {success_count}/{total_count} 个配置修改成功")
    
    if success_count > 0:
        print_success("🎉 SessionID 修改完成!")
        print_info("📋 注意事项:")
        print_info("1. 请重启 JetBrains 产品以使配置生效")
        print_info("2. 原配置文件已备份（如果存在）")
        print_info("3. 如需恢复，可以删除相关配置或使用备份文件")
        return True
    else:
        print_error("所有 JetBrains 产品的 SessionID 修改都失败了")
        return False
