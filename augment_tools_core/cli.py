import click
from pathlib import Path

# Assuming other modules are in the same package (augment_tools_core)
from .common_utils import (
    get_os_specific_vscode_paths,
    print_info,
    print_success,
    print_error,
    print_warning,
    IDEType,
    get_ide_display_name
)
from .database_manager import clean_ide_database, clean_vscode_database
from .telemetry_manager import modify_ide_telemetry_ids, modify_vscode_telemetry_ids

def parse_ide_type(ide_name: str) -> IDEType:
    """Parse IDE name string to IDEType enum"""
    ide_name_lower = ide_name.lower()
    if ide_name_lower in ['vscode', 'vs-code', 'code']:
        return IDEType.VSCODE
    elif ide_name_lower in ['cursor']:
        return IDEType.CURSOR
    elif ide_name_lower in ['windsurf']:
        return IDEType.WINDSURF
    else:
        raise click.BadParameter(f"Unsupported IDE: {ide_name}. Supported: vscode, cursor, windsurf")

@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def main_cli():
    """
    AugmentCode-Free: Multi-IDE Maintenance Tools.
    Provides utilities for cleaning IDE databases and modifying telemetry IDs.
    Supports VS Code, Cursor, and Windsurf.
    """
    pass

@main_cli.command("clean-db")
@click.option('--ide', default='vscode', show_default=True, 
              help='IDE to clean (vscode, cursor, windsurf)')
@click.option('--keyword', default='augment', show_default=True, 
              help='Keyword to search for and remove from the database (case-insensitive).')
def clean_db_command(ide: str, keyword: str):
    """Cleans the specified IDE's state database by removing entries matching the keyword."""
    try:
        ide_type = parse_ide_type(ide)
        ide_name = get_ide_display_name(ide_type)
        
        print_info(f"Executing: {ide_name} Database Cleaning (keyword: '{keyword}')")
        
        if clean_ide_database(ide_type, keyword):
            print_info("Database cleaning process finished.") 
        else:
            print_error("Database cleaning process reported errors. Check previous messages.")
            
    except click.BadParameter as e:
        print_error(str(e))
        return

@main_cli.command("modify-ids")
@click.option('--ide', default='vscode', show_default=True,
              help='IDE to modify (vscode, cursor, windsurf)')
def modify_ids_command(ide: str):
    """Modifies the specified IDE's telemetry IDs (machineId, devDeviceId) in storage.json."""
    try:
        ide_type = parse_ide_type(ide)
        ide_name = get_ide_display_name(ide_type)
        
        print_info(f"Executing: {ide_name} Telemetry ID Modification")
        
        if modify_ide_telemetry_ids(ide_type):
            print_info("Telemetry ID modification process finished.")
        else:
            print_error("Telemetry ID modification process reported errors. Check previous messages.")
            
    except click.BadParameter as e:
        print_error(str(e))
        return

@main_cli.command("run-all")
@click.option('--ide', default='vscode', show_default=True,
              help='IDE to process (vscode, cursor, windsurf)')
@click.option('--keyword', default='augment', show_default=True, 
              help='Keyword for database cleaning (case-insensitive).')
@click.pass_context
def run_all_command(ctx, ide: str, keyword: str):
    """Runs all available tools for the specified IDE: clean-db and then modify-ids."""
    try:
        ide_type = parse_ide_type(ide)
        ide_name = get_ide_display_name(ide_type)
        
        print_info(f"Executing: Run All Tools for {ide_name}")
        
        print_info(f"--- Step 1: {ide_name} Database Cleaning ---")
        try:
            ctx.invoke(clean_db_command, ide=ide, keyword=keyword)
        except Exception as e:
            print_error(f"An error occurred during database cleaning step: {e}")
            print_warning("Proceeding to the next step despite the error.")
        
        print_info(f"--- Step 2: {ide_name} Telemetry ID Modification ---")
        try:
            ctx.invoke(modify_ids_command, ide=ide)
        except Exception as e:
            print_error(f"An error occurred during telemetry ID modification step: {e}")

        print_success(f"All tools for {ide_name} have finished their execution sequence.")
        
    except click.BadParameter as e:
        print_error(str(e))
        return

# Legacy commands for backward compatibility
@main_cli.command("clean-vscode-db", hidden=True)
@click.option('--keyword', default='augment', show_default=True, help='Keyword to search for and remove from the database (case-insensitive).')
def clean_vscode_db_command(keyword: str):
    """[DEPRECATED] Use 'clean-db --ide vscode' instead."""
    print_warning("This command is deprecated. Use 'clean-db --ide vscode' instead.")
    ctx = click.get_current_context()
    ctx.invoke(clean_db_command, ide='vscode', keyword=keyword)

@main_cli.command("modify-vscode-ids", hidden=True)
def modify_vscode_ids_command():
    """[DEPRECATED] Use 'modify-ids --ide vscode' instead."""
    print_warning("This command is deprecated. Use 'modify-ids --ide vscode' instead.")
    ctx = click.get_current_context()
    ctx.invoke(modify_ids_command, ide='vscode')

if __name__ == '__main__':
    main_cli()
