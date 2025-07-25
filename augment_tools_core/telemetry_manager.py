import json
from pathlib import Path
import shutil

from .common_utils import (
    print_info, print_success, print_error, print_warning, create_backup,
    generate_new_machine_id, generate_new_device_id,
    IDEType, get_ide_paths, get_ide_display_name
)
from .jetbrains_manager import modify_all_jetbrains_session_ids

def modify_ide_telemetry_ids(ide_type: IDEType) -> bool:
    """
    Modifies the specified IDE's telemetry IDs (machineId and devDeviceId) in storage.json.

    Args:
        ide_type: The IDE type to modify

    Returns:
        True if modification was successful, False otherwise.
    """
    ide_name = get_ide_display_name(ide_type)
    print_info(f"开始修改 {ide_name} 遥测 ID")

    # JetBrains 产品使用不同的处理方式
    if ide_type == IDEType.JETBRAINS:
        return modify_all_jetbrains_session_ids()

    paths = get_ide_paths(ide_type)
    if not paths:
        print_error(f"无法确定 {ide_name} 路径。操作中止。")
        return False

    storage_path = paths.get("storage_json")
    if not storage_path:
        print_error(f"在配置中未找到 {ide_name} storage.json 路径。操作中止。")
        return False

    return modify_vscode_telemetry_ids(storage_path)

def modify_vscode_telemetry_ids(storage_json_path: Path) -> bool:
    """
    Modifies the telemetry IDs (machineId and devDeviceId) in storage.json.

    Args:
        storage_json_path: Path to the storage.json file.

    Returns:
        True if modification was successful, False otherwise.
    """
    print_info(f"尝试修改遥测 ID: {storage_json_path}")

    if not storage_json_path.exists():
        print_error(f"存储文件未找到: {storage_json_path}")
        print_info("故障排除建议:")
        print_info("1. 确保 IDE 已正确安装并至少运行过一次")
        print_info("2. 检查 IDE 是否已完全关闭")
        print_info("3. 验证用户权限是否足够访问配置目录")

        # 检查父目录是否存在
        parent_dir = storage_json_path.parent
        if parent_dir.exists():
            print_info(f"父目录存在: {parent_dir}")
            try:
                files_in_parent = list(parent_dir.iterdir())
                if files_in_parent:
                    print_info("父目录中的文件:")
                    for file in files_in_parent[:10]:  # 只显示前10个文件
                        print_info(f"  - {file.name}")
                    if len(files_in_parent) > 10:
                        print_info(f"  ... 还有 {len(files_in_parent) - 10} 个文件")
                else:
                    print_warning("父目录为空")
            except PermissionError:
                print_warning("无法访问父目录内容 (权限不足)")
        else:
            print_error(f"父目录不存在: {parent_dir}")

        return False

    backup_path = create_backup(storage_json_path)
    if not backup_path:
        print_error("创建备份失败。中止遥测 ID 修改。")
        return False

    try:
        # Generate new IDs
        new_machine_id = generate_new_machine_id()
        new_device_id = generate_new_device_id()
        
        print_info(f"生成新的 machineId: {new_machine_id}")
        print_info(f"生成新的 devDeviceId: {new_device_id}")

        # Read the JSON file
        with open(storage_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Modify the IDs
        modified = False
        if 'machineId' in data:
            if data['machineId'] != new_machine_id:
                data['machineId'] = new_machine_id
                print_info("更新了根级 machineId。")
                modified = True
            else:
                print_info("根级 machineId 已经是新值。")

        if 'telemetry' in data and isinstance(data['telemetry'], dict):
            if 'machineId' in data['telemetry']:
                if data['telemetry']['machineId'] != new_machine_id:
                    data['telemetry']['machineId'] = new_machine_id
                    print_info("更新了遥测 machineId。")
                    modified = True
                else:
                    print_info("遥测 machineId 已经是新值。")
            
            if 'devDeviceId' in data['telemetry']:
                if data['telemetry']['devDeviceId'] != new_device_id:
                    data['telemetry']['devDeviceId'] = new_device_id
                    print_info("更新了 devDeviceId。")
                    modified = True
                else:
                    print_info("devDeviceId 已经是新值。")

        if not modified:
            print_info("未找到相关遥测 ID 或 ID 已经匹配新值。内容未更改。")
            return True

        # Write the modified data back to the file
        with open(storage_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        print_success(f"成功修改遥测 ID: {storage_json_path}")
        return True

    except json.JSONDecodeError as e:
        print_error(f"处理 {storage_json_path} 时 JSON 解码错误: {e}")
    except IOError as e:
        print_error(f"处理 {storage_json_path} 时 IO 错误: {e}")
    except Exception as e:
        print_error(f"遥测 ID 修改过程中发生意外错误: {e}")

    # If any error occurred, attempt to restore from backup
    if backup_path and backup_path.exists():
        print_info(f"尝试从备份恢复存储文件: {backup_path}")
        try:
            shutil.copy2(backup_path, storage_json_path)
            print_success("存储文件已从备份成功恢复。")
        except Exception as restore_e:
            print_error(f"从备份恢复存储文件失败: {restore_e}")
    return False

if __name__ == '__main__':
    print_info("Testing telemetry_manager.py...")
    dummy_storage_path = Path("test_storage.json").resolve()
    original_content = {
        "machineId": "old_machine_id_root",
        "some_other_key": "value",
        "telemetry": {
            "machineId": "old_machine_id_telemetry",
            "devDeviceId": "old_dev_device_id",
            "another_telemetry_key": "value"
        }
    }

    try:
        # Create dummy storage.json
        with open(dummy_storage_path, 'w', encoding='utf-8') as f:
            json.dump(original_content, f, indent=4)
        print_success(f"Created dummy storage file '{dummy_storage_path}' with test data.")

        # Store original IDs for comparison
        original_machine_id_root = original_content.get("machineId")
        original_machine_id_telemetry = original_content.get("telemetry", {}).get("machineId")
        original_dev_device_id = original_content.get("telemetry", {}).get("devDeviceId")

        # Test modification
        modify_result = modify_vscode_telemetry_ids(dummy_storage_path)

        if modify_result:
            print_success("Telemetry ID modification test completed successfully.")
            # Verify content
            with open(dummy_storage_path, 'r', encoding='utf-8') as f:
                updated_data = json.load(f)
            
            new_machine_id_root = updated_data.get("machineId")
            new_machine_id_telemetry = updated_data.get("telemetry", {}).get("machineId")
            new_dev_device_id = updated_data.get("telemetry", {}).get("devDeviceId")

            error_found = False
            if new_machine_id_root == original_machine_id_root:
                print_error("Verification failed: Root machineId was not updated.")
                error_found = True
            
            if new_machine_id_telemetry == original_machine_id_telemetry:
                print_error("Verification failed: telemetry.machineId was not updated.")
                error_found = True

            if new_dev_device_id == original_dev_device_id:
                print_error("Verification failed: telemetry.devDeviceId was not updated.")
                error_found = True
            
            if not error_found:
                print_success("Verification successful: Telemetry IDs appear to have been updated.")
                print_info(f"  New root machineId: {new_machine_id_root}")
                print_info(f"  New telemetry.machineId: {new_machine_id_telemetry}")
                print_info(f"  New telemetry.devDeviceId: {new_dev_device_id}")

        else:
            print_error("Telemetry ID modification test failed.")
            
    except Exception as e:
        print_error(f"Error during test setup or execution: {e}")
    finally:
        # Clean up dummy db and its backup
        if dummy_storage_path.exists():
            dummy_storage_path.unlink()
        backup_dummy_path = dummy_storage_path.with_suffix(dummy_storage_path.suffix + ".backup")
        if backup_dummy_path.exists():
            backup_dummy_path.unlink()
        print_info("telemetry_manager.py tests complete and cleaned up.")
