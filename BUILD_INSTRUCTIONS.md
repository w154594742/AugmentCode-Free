# AugmentCode-Free v1.0.5 构建说明 / Build Instructions

## Windows 平台 ✅ 已完成 / Windows Platform ✅ Completed

已成功构建 / Successfully built:
- `AugmentCode-Free-v1.0.5.exe` (36.9 MB) - Windows 可执行文件 / Windows executable
- `AugmentCode-Free-v1.0.5-Portable.zip` (59 KB) - 跨平台便携包 / Cross-platform portable package

## macOS 平台构建 / macOS Platform Build

在 macOS 系统上执行以下命令 / Execute the following commands on macOS:

```bash
# 安装依赖 / Install dependencies
pip install pyinstaller PyQt6 psutil click colorama

# 构建 macOS 应用 / Build macOS application
pyinstaller --onefile --windowed \
    --name AugmentCode-Free-v1.0.5 \
    --distpath dist \
    --add-data "augment_tools_core:augment_tools_core" \
    --add-data "gui_qt6:gui_qt6" \
    --add-data "languages:languages" \
    --add-data "config:config" \
    --hidden-import PyQt6 \
    --hidden-import PyQt6.QtWidgets \
    --hidden-import PyQt6.QtCore \
    --hidden-import PyQt6.QtGui \
    --hidden-import psutil \
    --hidden-import xml.etree.ElementTree \
    main.py

# 创建 DMG 包（可选）/ Create DMG package (optional)
# 需要安装 create-dmg: brew install create-dmg
# Requires create-dmg: brew install create-dmg
create-dmg \
    --volname "AugmentCode-Free v1.0.5" \
    --window-pos 200 120 \
    --window-size 600 300 \
    --icon-size 100 \
    --icon "AugmentCode-Free-v1.0.5.app" 175 120 \
    --hide-extension "AugmentCode-Free-v1.0.5.app" \
    --app-drop-link 425 120 \
    "AugmentCode-Free-v1.0.5.dmg" \
    "dist/"
```

## Linux 平台构建 / Linux Platform Build

在 Linux 系统上执行以下命令 / Execute the following commands on Linux:

```bash
# 安装系统依赖（Ubuntu/Debian）/ Install system dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install python3-pip python3-venv
sudo apt install libxcb-xinerama0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
                 libxcb-keysyms1 libxcb-render-util0 libxcb-shape0 libxcb-util1 \
                 libxcb-xkb1 libxkbcommon-x11-0

# 创建虚拟环境 / Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 安装 Python 依赖 / Install Python dependencies
pip install pyinstaller PyQt6 psutil click colorama

# 构建 Linux 可执行文件 / Build Linux executable
pyinstaller --onefile \
    --name AugmentCode-Free-v1.0.5 \
    --distpath dist \
    --add-data "augment_tools_core:augment_tools_core" \
    --add-data "gui_qt6:gui_qt6" \
    --add-data "languages:languages" \
    --add-data "config:config" \
    --hidden-import PyQt6 \
    --hidden-import PyQt6.QtWidgets \
    --hidden-import PyQt6.QtCore \
    --hidden-import PyQt6.QtGui \
    --hidden-import psutil \
    --hidden-import xml.etree.ElementTree \
    main.py

# 创建 AppImage（可选）/ Create AppImage (optional)
# 需要下载 appimagetool / Download appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# 创建 AppDir 结构 / Create AppDir structure
mkdir -p AugmentCode-Free.AppDir/usr/bin
mkdir -p AugmentCode-Free.AppDir/usr/share/applications
mkdir -p AugmentCode-Free.AppDir/usr/share/icons/hicolor/256x256/apps

# 复制可执行文件 / Copy executable
cp dist/AugmentCode-Free-v1.0.5 AugmentCode-Free.AppDir/usr/bin/

# 创建 .desktop 文件 / Create .desktop file
cat > AugmentCode-Free.AppDir/AugmentCode-Free.desktop << EOF
[Desktop Entry]
Type=Application
Name=AugmentCode-Free
Exec=AugmentCode-Free-v1.0.5
Icon=augmentcode-free
Categories=Development;
EOF

# 创建 AppRun 脚本 / Create AppRun script
cat > AugmentCode-Free.AppDir/AppRun << EOF
#!/bin/bash
cd "\$(dirname "\$0")"
exec ./usr/bin/AugmentCode-Free-v1.0.5 "\$@"
EOF
chmod +x AugmentCode-Free.AppDir/AppRun

# 构建 AppImage / Build AppImage
./appimagetool-x86_64.AppImage AugmentCode-Free.AppDir AugmentCode-Free-v1.0.5-x86_64.AppImage
```

## 构建验证 / Build Verification

构建完成后，请验证以下功能 / After building, please verify the following functions:

1. **启动测试 / Startup Test**: 程序能正常启动并显示GUI / Program starts normally and displays GUI
2. **IDE检测 / IDE Detection**: 能正确检测已安装的IDE / Correctly detects installed IDEs
3. **功能测试 / Function Test**:
   - VS Code/Cursor/Windsurf 数据库清理 / Database cleaning
   - 遥测ID修改 / Telemetry ID modification
   - JetBrains SessionID修改 / JetBrains SessionID modification
4. **多语言 / Multi-language**: 中英文界面切换正常 / Chinese/English interface switching works properly
5. **进程检测 / Process Detection**: 能正确检测运行中的IDE进程 / Correctly detects running IDE processes

## 发布清单 / Release Checklist

每个平台需要提供 / Each platform should provide:

- **Windows**:
  - `AugmentCode-Free-v1.0.5.exe` ✅
  - `AugmentCode-Free-v1.0.5-Portable.zip` ✅

- **macOS**:
  - `AugmentCode-Free-v1.0.5.app` (或 .dmg / or .dmg)
  - 便携包已包含在 Windows 构建中 / Portable package included in Windows build

- **Linux**:
  - `AugmentCode-Free-v1.0.5` (可执行文件 / executable)
  - `AugmentCode-Free-v1.0.5-x86_64.AppImage` (可选 / optional)
  - 便携包已包含在 Windows 构建中 / Portable package included in Windows build

## 注意事项 / Important Notes

1. **依赖管理 / Dependency Management**: 确保所有平台都包含必要的系统依赖 / Ensure all platforms include necessary system dependencies
2. **权限设置 / Permission Settings**: Linux/macOS 可执行文件需要执行权限 / Linux/macOS executables need execute permissions
3. **代码签名 / Code Signing**: macOS 可能需要代码签名以避免安全警告 / macOS may require code signing to avoid security warnings
4. **测试环境 / Testing Environment**: 在干净的系统上测试以确保依赖完整性 / Test on clean systems to ensure dependency integrity
