import click
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

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

# Import language management
try:
    from language_manager import get_language_manager, get_text
    from config_manager import get_config_manager
    LANGUAGE_SUPPORT = True
except ImportError:
    LANGUAGE_SUPPORT = False
    def get_text(key, **kwargs):
        return key

def parse_ide_type(ide_name: str) -> IDEType:
    """Parse IDE name string to IDEType enum"""
    ide_name_lower = ide_name.lower()
    if ide_name_lower in ['vscode', 'vs-code', 'code']:
        return IDEType.VSCODE
    elif ide_name_lower in ['cursor']:
        return IDEType.CURSOR
    elif ide_name_lower in ['windsurf']:
        return IDEType.WINDSURF
    elif ide_name_lower in ['jetbrains', 'pycharm', 'intellij', 'idea', 'webstorm', 'phpstorm']:
        return IDEType.JETBRAINS
    else:
        raise click.BadParameter(get_text("cli.unsupported_ide", ide=ide_name))

@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--language', default=None, help='Set language (zh_CN, en_US)')
def main_cli(language):
    """
    AugmentCode-Free: Multi-IDE Maintenance Tools.
    Provides utilities for cleaning IDE databases and modifying telemetry IDs.
    Supports VS Code, Cursor, and Windsurf.
    """
    if LANGUAGE_SUPPORT and language:
        config_manager = get_config_manager()
        language_manager = get_language_manager(config_manager)
        language_manager.set_language(language)

@main_cli.command("clean-db")
@click.option('--ide', default='vscode', show_default=True,
              help=get_text("cli.ide_option_help"))
@click.option('--keyword', default='augment', show_default=True,
              help=get_text("cli.keyword_option_help"))
def clean_db_command(ide: str, keyword: str):
    """Cleans the specified IDE's state database by removing entries matching the keyword."""
    try:
        ide_type = parse_ide_type(ide)
        ide_name = get_ide_display_name(ide_type)

        print_info(get_text("cli.executing", operation=f"{ide_name} Database Cleaning (keyword: '{keyword}')"))

        if clean_ide_database(ide_type, keyword):
            print_info(get_text("cli.finished"))
        else:
            print_error(get_text("cli.errors"))

    except click.BadParameter as e:
        print_error(str(e))
        return

@main_cli.command("modify-ids")
@click.option('--ide', default='vscode', show_default=True,
              help=get_text("cli.ide_option_help"))
def modify_ids_command(ide: str):
    """Modifies the specified IDE's telemetry IDs (machineId, devDeviceId) in storage.json."""
    try:
        ide_type = parse_ide_type(ide)
        ide_name = get_ide_display_name(ide_type)

        print_info(get_text("cli.executing", operation=f"{ide_name} Telemetry ID Modification"))

        if modify_ide_telemetry_ids(ide_type):
            print_info(get_text("cli.finished"))
        else:
            print_error(get_text("cli.errors"))

    except click.BadParameter as e:
        print_error(str(e))
        return

@main_cli.command("run-all")
@click.option('--ide', default='vscode', show_default=True,
              help=get_text("cli.ide_option_help"))
@click.option('--keyword', default='augment', show_default=True,
              help=get_text("cli.keyword_clean_help"))
@click.pass_context
def run_all_command(ctx, ide: str, keyword: str):
    """Runs all available tools for the specified IDE: clean-db and then modify-ids."""
    try:
        ide_type = parse_ide_type(ide)
        ide_name = get_ide_display_name(ide_type)

        print_info(get_text("cli.executing", operation=f"Run All Tools for {ide_name}"))

        print_info(get_text("cli.step", step="1", operation=f"{ide_name} Database Cleaning"))
        try:
            ctx.invoke(clean_db_command, ide=ide, keyword=keyword)
        except Exception as e:
            print_error(get_text("cli.error_occurred", step="database cleaning", error=str(e)))
            print_warning(get_text("cli.proceeding"))

        print_info(get_text("cli.step", step="2", operation=f"{ide_name} Telemetry ID Modification"))
        try:
            ctx.invoke(modify_ids_command, ide=ide)
        except Exception as e:
            print_error(get_text("cli.error_occurred", step="telemetry ID modification", error=str(e)))

        print_success(get_text("cli.all_finished", ide_name=ide_name))

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
