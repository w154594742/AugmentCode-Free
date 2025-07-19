# AugmentCode-Free v1.0.1 发布说明 / Release Notes

<p align="center">
  <a href="#中文版本">🇨🇳 中文版本</a> | <a href="#english-version">🇺🇸 English Version</a>
</p>

---

## 🇨🇳 中文版本 {#中文版本}

### 🐛 紧急修复版本

**AugmentCode-Free v1.0.1** 是一个重要的修复版本，解决了影响Cursor和Windsurf IDE用户的关键路径配置问题。

### 🔧 修复内容

#### 关键Bug修复
- **修复Cursor IDE Windows路径配置错误**
  - 问题：工具无法在Windows系统上正确定位Cursor IDE配置文件
  - 修复：更正路径为 `%APPDATA%\Cursor\User\globalStorage\`
  - 影响：确保数据库清理和遥测ID修改功能正常工作

- **修复Windsurf IDE Windows路径配置错误**
  - 问题：工具使用了错误的Windsurf配置目录
  - 修复：更正主目录为 `~/.codeium/windsurf/`
  - 影响：Windsurf用户现在可以正常使用所有维护功能

#### 改进内容
- **增强错误处理**：添加APPDATA环境变量检查
- **改进用户提示**：提供更详细的错误信息
- **代码注释**：添加路径配置说明注释

### ⚠️ 重要性
这是一个**关键修复版本**，强烈建议所有用户立即更新，特别是：
- 使用Cursor IDE的用户
- 使用Windsurf IDE的用户
- 在Windows系统上运行工具的用户

### 📥 下载和更新

#### 已安装用户（推荐）
```bash
pip install --upgrade augment-tools-core
```

#### 新用户安装
```bash
pip install augment-tools-core
```

---

## 🇺🇸 English Version {#english-version}

### 🐛 Critical Hotfix Release

**AugmentCode-Free v1.0.1** is an important hotfix release that addresses critical path configuration issues affecting Cursor and Windsurf IDE users.

### 🔧 Fixes

#### Critical Bug Fixes
- **Fixed Cursor IDE Windows Path Configuration**
  - Issue: Tool couldn't locate Cursor IDE configuration files on Windows
  - Fix: Corrected path to `%APPDATA%\Cursor\User\globalStorage\`
  - Impact: Database cleaning and telemetry ID modification now work properly

- **Fixed Windsurf IDE Windows Path Configuration**
  - Issue: Tool used incorrect Windsurf configuration directory
  - Fix: Corrected main directory to `~/.codeium/windsurf/`
  - Impact: Windsurf users can now use all maintenance functions normally

#### Improvements
- **Enhanced Error Handling**: Added APPDATA environment variable checking
- **Improved User Feedback**: More detailed error messages
- **Code Documentation**: Added path configuration comments

### ⚠️ Importance
This is a **critical hotfix release**. All users are strongly recommended to update immediately, especially:
- Cursor IDE users
- Windsurf IDE users  
- Users running the tool on Windows systems

### 📥 Download and Update

#### Existing Users (Recommended)
```bash
pip install --upgrade augment-tools-core
```

#### New Users
```bash
pip install augment-tools-core
```

---

## 📊 构建信息 / Build Information

- **版本 / Version**: v1.0.1
- **发布类型 / Release Type**: Hotfix (紧急修复)
- **修复范围 / Fix Scope**: Windows路径配置 / Windows Path Configuration
- **影响用户 / Affected Users**: Cursor & Windsurf IDE用户 / Cursor & Windsurf IDE Users
- **优先级 / Priority**: 高 / High

---

## 🔄 升级说明 / Upgrade Notes

### 从 v1.0.0 升级
- 无需额外配置更改
- 自动修复路径配置问题
- 向后兼容所有现有功能

### From v1.0.0 Upgrade
- No additional configuration changes required
- Automatically fixes path configuration issues
- Backward compatible with all existing features
