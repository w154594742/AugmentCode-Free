#!/usr/bin/env python3
"""
AugmentCode-Free Cross-Platform Build System
简洁高效的跨平台应用打包工具

Usage:
    python build.py              # 构建当前平台
    python build.py --all        # 构建所有平台
    python build.py --clean      # 清理构建文件
    python build.py --verbose    # 详细输出
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
from pathlib import Path
from typing import Optional, Dict, List

# 项目配置
PROJECT_NAME = "AugmentCodeFree"
VERSION = "2.0.3"
AUTHOR = "BasicProtein"
DESCRIPTION = "多IDE维护工具包 - 支持VS Code、Cursor、Windsurf、JetBrains"

# 颜色输出
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_info(msg: str):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")

def print_success(msg: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {msg}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.END} {msg}")

def print_error(msg: str):
    print(f"{Colors.RED}[ERROR]{Colors.END} {msg}")

def print_step(msg: str):
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== {msg} ==={Colors.END}")

class PlatformDetector:
    """平台检测器"""
    
    @staticmethod
    def get_current_platform() -> str:
        """获取当前平台"""
        system = platform.system().lower()
        if system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        elif system == "linux":
            return "linux"
        else:
            return "unknown"
    
    @staticmethod
    def get_executable_extension(platform_name: str) -> str:
        """获取可执行文件扩展名"""
        if platform_name == "windows":
            return ".exe"
        elif platform_name == "macos":
            return ".app"
        else:
            return ""

class DependencyChecker:
    """依赖检查器"""
    
    @staticmethod
    def check_pyinstaller() -> bool:
        """检查PyInstaller是否安装"""
        try:
            result = subprocess.run(
                ["pyinstaller", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                print_success(f"PyInstaller已安装: {version}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        print_error("PyInstaller未安装")
        print_info("请运行: pip install pyinstaller")
        return False
    
    @staticmethod
    def check_python_version() -> bool:
        """检查Python版本"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 7:
            print_success(f"Python版本: {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            print_error(f"Python版本过低: {version.major}.{version.minor}.{version.micro}")
            print_info("需要Python 3.7或更高版本")
            return False

class ExecutableBuilder:
    """可执行文件构建器"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.project_root = Path.cwd()
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
    
    def clean_build_files(self):
        """清理构建文件"""
        print_step("清理构建文件")
        
        # 清理目录
        for dir_path in [self.dist_dir, self.build_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print_info(f"已删除: {dir_path}")
        
        # 清理spec文件
        for spec_file in self.project_root.glob("*.spec"):
            spec_file.unlink()
            print_info(f"已删除: {spec_file}")
        
        print_success("构建文件清理完成")
    
    def create_pyinstaller_spec(self, platform_name: str) -> str:
        """创建PyInstaller配置文件"""
        app_name = f"{PROJECT_NAME}-v{VERSION}-{platform_name}"
        spec_content = self._generate_spec_content(app_name, platform_name)
        
        spec_file = self.project_root / f"{app_name}.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print_success(f"已创建配置文件: {spec_file.name}")
        return str(spec_file)

    def _generate_spec_content(self, app_name: str, platform_name: str) -> str:
        """生成PyInstaller配置内容"""
        # 基础配置
        console_mode = "False" if platform_name == "macos" else "True"

        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# {PROJECT_NAME} v{VERSION} PyInstaller配置
# 平台: {platform_name}

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('augment_tools_core', 'augment_tools_core'),
        ('gui_qt6', 'gui_qt6'),
        ('languages', 'languages'),
        ('config', 'config'),
        ('README.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'PyQt6', 'PyQt6.QtWidgets', 'PyQt6.QtCore', 'PyQt6.QtGui',
        'click', 'colorama', 'pathlib', 'sqlite3', 'json', 'uuid',
        'platform', 'subprocess', 'threading', 'queue', 'time', 'psutil',
        'xml.etree.ElementTree', 'shutil', 'tempfile'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'PIL'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='{app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console_mode},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)'''

        # macOS特定配置
        if platform_name == "macos":
            spec_content += f'''

app = BUNDLE(
    exe,
    name='{app_name}.app',
    icon=None,
    bundle_identifier='com.{AUTHOR.lower()}.{PROJECT_NAME.lower()}',
    info_plist={{
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '{VERSION}',
        'CFBundleVersion': '{VERSION}',
        'CFBundleDisplayName': '{PROJECT_NAME}',
        'CFBundleName': '{PROJECT_NAME}',
    }},
)'''

        return spec_content

    def build_executable(self, platform_name: str) -> bool:
        """构建可执行文件"""
        print_step(f"构建 {platform_name.title()} 可执行文件")

        try:
            # 创建配置文件
            spec_file = self.create_pyinstaller_spec(platform_name)

            # 准备PyInstaller参数
            cmd = ["pyinstaller", spec_file, "--clean", "--noconfirm"]

            # 设置输出目录
            platform_dist_dir = self.dist_dir / platform_name
            cmd.extend(["--distpath", str(platform_dist_dir)])

            print_info(f"执行命令: {' '.join(cmd)}")

            # 执行构建
            result = subprocess.run(
                cmd,
                capture_output=not self.verbose,
                text=True,
                timeout=600
            )

            if result.returncode != 0:
                print_error("PyInstaller构建失败")
                if not self.verbose and result.stderr:
                    print_error(f"错误信息: {result.stderr}")
                return False

            # 验证输出文件
            return self._verify_build_output(platform_name, platform_dist_dir)

        except subprocess.TimeoutExpired:
            print_error("构建超时（10分钟）")
            return False
        except Exception as e:
            print_error(f"构建过程出错: {e}")
            return False
        finally:
            # 清理spec文件
            spec_file_path = Path(spec_file)
            if spec_file_path.exists():
                spec_file_path.unlink()

    def _verify_build_output(self, platform_name: str, dist_dir: Path) -> bool:
        """验证构建输出"""
        app_name = f"{PROJECT_NAME}-v{VERSION}-{platform_name}"
        extension = PlatformDetector.get_executable_extension(platform_name)
        expected_file = dist_dir / f"{app_name}{extension}"

        if not expected_file.exists():
            print_error(f"未找到预期的输出文件: {expected_file}")
            # 列出实际生成的文件
            if dist_dir.exists():
                print_info("实际生成的文件:")
                for item in dist_dir.iterdir():
                    print_info(f"  - {item.name}")
            return False

        # 计算文件大小
        if expected_file.is_file():
            size = expected_file.stat().st_size
            size_mb = size / (1024 * 1024)
            print_success(f"构建成功: {expected_file.name} ({size_mb:.2f} MB)")
        else:
            # 对于.app包，计算总大小
            total_size = sum(f.stat().st_size for f in expected_file.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            print_success(f"构建成功: {expected_file.name} ({size_mb:.2f} MB)")

        return True

class CrossPlatformBuilder:
    """跨平台构建协调器"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.builder = ExecutableBuilder(verbose)
        self.current_platform = PlatformDetector.get_current_platform()

    def build_current_platform(self) -> bool:
        """构建当前平台"""
        print_step(f"开始构建当前平台: {self.current_platform.title()}")
        return self.builder.build_executable(self.current_platform)

    def build_all_platforms(self) -> Dict[str, bool]:
        """构建所有平台（仅当前平台实际可构建）"""
        print_step("开始跨平台构建")
        print_warning("注意: 只能构建当前运行平台的可执行文件")

        results = {}
        platforms = ["windows", "macos", "linux"]

        for platform_name in platforms:
            if platform_name == self.current_platform:
                print_info(f"构建 {platform_name} (当前平台)")
                results[platform_name] = self.builder.build_executable(platform_name)
            else:
                print_warning(f"跳过 {platform_name} (需要在对应平台上构建)")
                results[platform_name] = False

        return results

    def clean_all(self):
        """清理所有构建文件"""
        self.builder.clean_build_files()

def print_banner():
    """打印程序横幅"""
    print(f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                AugmentCode-Free Build System                 ║
║                     跨平台应用打包工具                        ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
项目: {PROJECT_NAME} v{VERSION}
作者: {AUTHOR}
描述: {DESCRIPTION}
""")

def print_build_summary(results: Dict[str, bool]):
    """打印构建摘要"""
    print_step("构建摘要")

    success_count = sum(1 for success in results.values() if success)
    total_count = len([r for r in results.values() if r is not False])

    for platform, success in results.items():
        if success:
            print_success(f"{platform}: 构建成功")
        elif success is False and platform in ["windows", "macos", "linux"]:
            print_warning(f"{platform}: 跳过（需要在对应平台构建）")
        else:
            print_error(f"{platform}: 构建失败")

    if success_count > 0:
        print_success(f"总计: {success_count}/{total_count} 个平台构建成功")
        print_info("构建的文件位于 dist/ 目录中")
    else:
        print_error("没有成功构建任何平台")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AugmentCode-Free 跨平台构建工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python build.py              构建当前平台
  python build.py --all        构建所有平台
  python build.py --clean      清理构建文件
  python build.py --verbose    详细输出
        """
    )

    parser.add_argument("--all", action="store_true", help="构建所有平台")
    parser.add_argument("--clean", action="store_true", help="清理构建文件")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    print_banner()

    # 检查依赖
    if not DependencyChecker.check_python_version():
        sys.exit(1)

    if not args.clean and not DependencyChecker.check_pyinstaller():
        sys.exit(1)

    # 创建构建器
    builder = CrossPlatformBuilder(verbose=args.verbose)

    try:
        if args.clean:
            builder.clean_all()
            print_success("清理完成")
            return

        # 执行构建
        if args.all:
            results = builder.build_all_platforms()
            print_build_summary(results)
        else:
            success = builder.build_current_platform()
            if success:
                print_success("构建完成！")
                print_info("构建的文件位于 dist/ 目录中")
            else:
                print_error("构建失败")
                sys.exit(1)

    except KeyboardInterrupt:
        print_warning("\n构建被用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"构建过程出现未预期的错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
