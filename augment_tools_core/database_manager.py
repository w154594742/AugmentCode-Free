import sqlite3
import shutil
from pathlib import Path
import logging
from .common_utils import (
    print_info, print_success, print_warning, print_error, create_backup,
    IDEType, get_ide_paths, get_ide_display_name
)

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_ide_database(ide_type: IDEType, keyword: str = "augment") -> bool:
    """
    Cleans the specified IDE's SQLite database by removing entries containing a specific keyword.

    Args:
        ide_type: The IDE type to clean
        keyword: The keyword to search for in the 'key' column of 'ItemTable'.
                 Entries containing this keyword will be removed.

    Returns:
        True if the database was cleaned successfully or if no cleaning was needed,
        False otherwise.
    """
    ide_name = get_ide_display_name(ide_type)
    print_info(f"开始清理 {ide_name} 数据库 (关键字: '{keyword}')")

    # JetBrains 产品不需要数据库清理，直接返回成功
    if ide_type == IDEType.JETBRAINS:
        print_info(f"{ide_name} 产品不需要数据库清理，跳过此步骤")
        return True

    paths = get_ide_paths(ide_type)
    if not paths:
        print_error(f"无法确定 {ide_name} 路径。操作中止。")
        return False
    
    db_path = paths.get("state_db")
    if not db_path:
        print_error(f"在配置中未找到 {ide_name} state.vscdb 路径。操作中止。")
        return False
    
    return clean_vscode_database(db_path, keyword)

def clean_vscode_database(db_path: Path, keyword: str = "augment") -> bool:
    """
    Cleans the SQLite database by removing entries containing a specific keyword.

    Args:
        db_path: Path to the state.vscdb SQLite database.
        keyword: The keyword to search for in the 'key' column of 'ItemTable'.
                 Entries containing this keyword will be removed.

    Returns:
        True if the database was cleaned successfully or if no cleaning was needed,
        False otherwise.
    """
    if not db_path.exists():
        print_error(f"数据库文件未找到: {db_path}")
        print_info("故障排除建议:")
        print_info("1. 确保 IDE 已正确安装并至少运行过一次")
        print_info("2. 检查 IDE 是否已完全关闭")
        print_info("3. 验证用户权限是否足够访问配置目录")

        # 检查父目录是否存在
        parent_dir = db_path.parent
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

    print_info(f"尝试清理数据库: {db_path}")
    print_info(f"目标清理关键字: '{keyword}'")

    backup_path = None
    try:
        # 1. Create a backup
        print_info("正在备份数据库...")
        backup_path = create_backup(db_path)
        if not backup_path:
            return False
        print_success(f"数据库备份成功: {backup_path}")

        # 2. Connect to the SQLite database
        print_info(f"连接到数据库: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print_success("成功连接到数据库。")

        # 3. Find and count entries to be deleted
        query_select = f"SELECT key FROM ItemTable WHERE key LIKE ?"
        like_pattern = f"%{keyword}%"
        
        print_info(f"搜索包含关键字 '{keyword}' 的条目...")
        cursor.execute(query_select, (like_pattern,))
        entries_to_delete = cursor.fetchall()
        
        num_entries_to_delete = len(entries_to_delete)

        if num_entries_to_delete == 0:
            print_success(f"未找到包含关键字 '{keyword}' 的条目。数据库已经是干净的。")
            conn.close()
            return True

        print_info(f"找到 {num_entries_to_delete} 个包含 '{keyword}' 的条目:")
        for entry in entries_to_delete[:5]:  # Show first 5 entries
            print_info(f"  - {entry[0]}")
        if num_entries_to_delete > 5:
            print_info(f"  ... 还有 {num_entries_to_delete - 5} 个条目")

        # 4. Delete the entries
        query_delete = f"DELETE FROM ItemTable WHERE key LIKE ?"
        print_info(f"正在删除包含 '{keyword}' 的条目...")
        cursor.execute(query_delete, (like_pattern,))
        conn.commit()
        
        deleted_rows = cursor.rowcount
        if deleted_rows == num_entries_to_delete:
            print_success(f"成功删除 {deleted_rows} 个包含 '{keyword}' 的条目。")
        else:
            print_warning(f"尝试删除 {num_entries_to_delete} 个条目，但数据库报告删除了 {deleted_rows} 个。")
            if deleted_rows > 0:
                 print_success(f"部分成功: 删除了 {deleted_rows} 个条目。")
            else:
                 print_error("尽管找到了条目，但没有删除任何条目。请检查数据库权限或日志。")
                 conn.close()
                 return False

        conn.close()
        print_success("数据库清理完成。")
        return True

    except sqlite3.Error as e:
        print_error(f"SQLite 错误: {e}")
        if backup_path and backup_path.exists():
            print_warning(f"尝试从备份恢复数据库: {backup_path}")
            try:
                shutil.copy2(backup_path, db_path)
                print_success("数据库已从备份成功恢复。")
            except Exception as restore_e:
                print_error(f"从备份恢复数据库失败: {restore_e}")
                print_error(f"原始数据库 {db_path} 可能已损坏或处于不一致状态。")
                print_error(f"备份文件位于: {backup_path}")
        return False
    except Exception as e:
        print_error(f"发生意外错误: {e}")
        return False

if __name__ == '__main__':
    # This is for direct testing of this module, not part of the CLI.
    print_info("Running database_manager.py directly for testing.")
    
    # --- IMPORTANT ---
    # For testing, you MUST provide a valid path to a VS Code state.vscdb file.
    # It's highly recommended to use a COPY of your actual state.vscdb for testing
    # to avoid accidental data loss in your VS Code setup.
    #
    # Example:
    # test_db_path = Path.home() / "AppData" / "Roaming" / "Code" / "User" / "globalStorage" / "state.vscdb" # Windows
    # test_db_path = Path.home() / ".config" / "Code" / "User" / "globalStorage" / "state.vscdb" # Linux
    # test_db_path = Path.home() / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "state.vscdb" # macOS

    # Create a dummy database for testing if you don't want to use a real one
    dummy_db_path = Path("./test_state.vscdb")
    
    # Create a copy for testing to avoid modifying the original dummy
    test_dummy_db_path = Path("./test_state_copy.vscdb")

    if dummy_db_path.exists():
        dummy_db_path.unlink() # Delete if exists from previous run

    conn_test = sqlite3.connect(dummy_db_path)
    cursor_test = conn_test.cursor()
    cursor_test.execute("CREATE TABLE IF NOT EXISTS ItemTable (key TEXT PRIMARY KEY, value BLOB)")
    test_data = [
        ("storage.testKey1", b"testValue1"),
        ("augment.testKey2", b"testValue2"),
        ("another.augment.key", b"testValue3"),
        ("noKeywordHere", b"testValue4"),
        ("prefix.augment", b"testValue5"),
    ]
    cursor_test.executemany("INSERT OR IGNORE INTO ItemTable VALUES (?, ?)", test_data)
    conn_test.commit()
    conn_test.close()
    print_success(f"Created dummy database at {dummy_db_path} with test data.")

    # Make a copy to test on
    shutil.copy2(dummy_db_path, test_dummy_db_path)
    print_info(f"Copied dummy database to {test_dummy_db_path} for cleaning test.")

    print_info("\n--- Test Case 1: Cleaning with default keyword 'augment' ---")
    if clean_vscode_database(test_dummy_db_path, keyword="augment"):
        print_success("Test Case 1: Cleaning successful.")
    else:
        print_error("Test Case 1: Cleaning failed.")

    # Verify content after cleaning
    conn_verify = sqlite3.connect(test_dummy_db_path)
    cursor_verify = conn_verify.cursor()
    cursor_verify.execute("SELECT key FROM ItemTable")
    remaining_keys = [row[0] for row in cursor_verify.fetchall()]
    print_info(f"Remaining keys in {test_dummy_db_path}: {remaining_keys}")
    expected_keys = ["storage.testKey1", "noKeywordHere"]
    assert all(k in remaining_keys for k in expected_keys) and len(remaining_keys) == len(expected_keys), \
        f"Test Case 1 Verification Failed! Expected {expected_keys}, got {remaining_keys}"
    print_success("Test Case 1: Verification successful.")
    conn_verify.close()


    print_info("\n--- Test Case 2: Cleaning with a keyword that finds nothing ('nonexistent') ---")
    # Re-copy the original dummy db for a fresh test
    shutil.copy2(dummy_db_path, test_dummy_db_path)
    if clean_vscode_database(test_dummy_db_path, keyword="nonexistent"):
        print_success("Test Case 2: Cleaning reported success (as expected, no items to clean).")
    else:
        print_error("Test Case 2: Cleaning failed.")
    
    conn_verify_2 = sqlite3.connect(test_dummy_db_path)
    cursor_verify_2 = conn_verify_2.cursor()
    cursor_verify_2.execute("SELECT COUNT(*) FROM ItemTable")
    count_after_no_keyword = cursor_verify_2.fetchone()[0]
    assert count_after_no_keyword == len(test_data), \
        f"Test Case 2 Verification Failed! Expected {len(test_data)} items, got {count_after_no_keyword}"
    print_success("Test Case 2: Verification successful (no items were deleted).")
    conn_verify_2.close()

    print_info("\n--- Test Case 3: Database file does not exist ---")
    non_existent_db_path = Path("./non_existent_db.vscdb")
    if non_existent_db_path.exists():
        non_existent_db_path.unlink() # Ensure it doesn't exist
        
    if not clean_vscode_database(non_existent_db_path):
        print_success("Test Case 3: Handled non-existent database file correctly (returned False).")
    else:
        print_error("Test Case 3: Failed to handle non-existent database file.")

    # Clean up dummy files
    if dummy_db_path.exists():
        dummy_db_path.unlink()
    if test_dummy_db_path.exists():
        test_dummy_db_path.unlink()
    print_info("\nCleaned up dummy database files.")
    print_success("All database_manager tests completed.")
