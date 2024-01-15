from pathlib import Path
from typing import Optional
from shutil import copy2
import os

import typer

from pygeonhole import (
    ERRORS, __app_name__, __version__, config, database, flags, pygeonhole
)
from pygeonhole import EXPORT_ERROR, PATH_ERROR

app = typer.Typer()

def get_PHC() -> pygeonhole.PH_Controller:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
        flags_path = flags.get_flags_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho('Config file not found. Please run "pygeonhole-cli init"', fg=typer.colors.RED)
        raise typer.Exit(1)
    if db_path.exists() and flags_path.exists():
        return pygeonhole.PH_Controller(db_path, flags_path)
    else:
        typer.secho('Database not found. Please run "pygeonhole-cli init"', fg=typer.colors.RED)
        raise typer.Exit(1)

"""
This function essentially resets the program (though it does not reset
the flags) so it is necessary to warn the user of adding and removing
files while in the middle of execution. Probably better to just tell
user to re-init.
"""
def update_db() -> None:
    phc = get_PHC()

    db_result = phc.get_db_data()
    if db_result.error:
        typer.secho(f'Displaying items failed with "{ERRORS[db_result.error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)

    dir_result = phc.get_dir_data()
    if dir_result.error:
        typer.secho(f'Displaying items failed with "{ERRORS[dir_result.error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)
    
    formatted_files = []
    for item in dir_result.dir_data:
        format_result = phc.format_item(item)
        if format_result.error:
            typer.secho(f'Update failed with "{ERRORS[format_result.error]}"', fg=typer.colors.RED)
            raise typer.Exit(1)
        formatted_files.append(format_result.item_data)

    write_result = phc.set_db_data(formatted_files)
    if write_result.error:
        typer.secho(f'Update failed with "{ERRORS[write_result.error]}"', fg=typer.colors.RED)
        raise typer.Exit(1)


def display_db() -> None:
    phc = get_PHC()

    db_result = phc.get_db_data()
    if db_result.error:
        typer.secho(f'Displaying items failed with "{ERRORS[db_result.error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)
    if len(db_result.data) == 0:
        typer.secho("There are no items in the directory", fg=typer.colors.RED)
        raise typer.Exit()

    data_lists = {}
    for key in db_result.data[0].keys():
        data_lists[key] = [item[key] for item in db_result.data]
    
    # Format table
    maxlen_id = len(str(len(db_result.data)))
    maxlen_keys = {}
    for key, value in data_lists.items():
        maxlen_keys[key] = max(len(max(value, key=len)), len(key))

        if key == "Name":
            maxlen_keys[key] += 1

    columns = ["#"]
    columns.extend(data_lists.keys())
    header = f"{columns[0]:<{maxlen_id}} |"
    for col in columns[1:]:
        header += f" {col:<{maxlen_keys[col]}} |"
    
    typer.secho(f'\n{database.CWD_PATH}:\n', fg=typer.colors.BLUE, bold=True)
    typer.secho(header, fg=typer.colors.BLUE, bold=True)
    typer.secho("-" * len(header), fg=typer.colors.BLUE)

    for id in range(1, len(db_result.data)+1):
        line = f"{id:<{maxlen_id}} |"
        for col in columns[1:]:
            str_literal = data_lists[col][id-1]
            spaces = maxlen_keys[col]

            if col == "Name" and data_lists["Mode"][id-1] == "drwxr-xr-x":
                str_literal += "/"

            line += f" {str_literal:<{spaces}} |"
        typer.secho(line, fg=typer.colors.BLUE)

    typer.secho("-" * len(header) + "\n", fg=typer.colors.BLUE)
    
@app.command()
def init() -> None:
    db_path = database.DEFAULT_DB_PATH
    flags_path = flags.DEFAULT_FLAGS_PATH

    app_init_error = config.init_app(db_path, flags_path)
    if app_init_error:
        typer.secho(f'Creating config file failed with "{ERRORS[app_init_error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)
    
    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(f'Creating database file failed with "{ERRORS[db_init_error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)
    
    flags_init_error = flags.init_flags(Path(flags_path))
    if flags_init_error:
        typer.secho(f'Creating flags file failed with "{ERRORS[flags_init_error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)
    
    typer.secho(f"The pigeonhole database is {db_path}", fg=typer.colors.GREEN)

    # Input files into database
    phc = get_PHC()

    dir_result = phc.get_dir_data()
    if dir_result.error:
        typer.secho(f'Initialization failed with "{ERRORS[dir_result.error]}"', fg=typer.colors.RED)
        raise typer.Exit(1)

    formatted_files = []
    for item in dir_result.dir_data:
        format_result = phc.format_item(item)
        if format_result.error:
            typer.secho(f'Initialization failed with "{ERRORS[format_result.error]}"', fg=typer.colors.RED)
            raise typer.Exit(1)
        formatted_files.append(format_result.item_data)

    write_result = phc.set_db_data(formatted_files)
    if write_result.error:
        typer.secho(f'Initialization failed with "{ERRORS[write_result.error]}"', fg=typer.colors.RED)
        raise typer.Exit(1)

    display_db()

@app.command()
def show(
    show_hidden: bool = typer.Option(False, "--hidden", "-a", help="Show hidden files and directories"),
    show_dirs: bool = typer.Option(False, "-d", help="Show directories"),
    repeat_show: bool = typer.Option(False, "--repeat", "-r", help="Display list after every command"),
) -> None:
    command_flags = locals().copy()
    phc = get_PHC()

    read_result = phc.get_flags_data()
    if read_result.error:
        typer.secho(f'Reading flags failed with "{ERRORS[read_result.error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)
    
    curr_flags = read_result.flags
    # Stored flags are inverted if they are called
    for flag in command_flags.keys():
        curr_flags[flag] = not curr_flags[flag] if command_flags[flag] else curr_flags[flag]

    write_result = phc.set_flags_data(curr_flags)
    if write_result.error:
        typer.secho(f'Writing flags failed with "{ERRORS[write_result.error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)
    
    update_db()
    display_db()

@app.command()
def format(
    
) -> None:
    phc = get_PHC()

    flag_result = phc.get_flags_data()
    if flag_result.error:
        typer.secho(f'Reading flags failed with "{ERRORS[flag_result.error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)
    

    if flag_result.flags["repeat_show"]:
        display_db()

@app.command()
def sort(
    sorting_key: str = typer.Argument(..., help="Name of column to sort"),
    reverse_order: bool = typer.Option(False, "--reverse", "-r", help="Reverse order of sort")
) -> None:
    phc = get_PHC()

    flag_result = phc.get_flags_data()
    if flag_result.error:
        typer.secho(f'Reading flags failed with "{ERRORS[flag_result.error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)
    
    db_result = phc.get_db_data()
    if db_result.error:
        typer.secho(f'Sorting items failed with "{ERRORS[db_result.error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)

    curr_db = db_result.data
    dirs = [item for item in curr_db if item["Mode"] == "drwxr-xr-x"]
    files = [item for item in curr_db if item["Mode"] == "-rw-r--r--"]
    dirs = sorted(dirs, key=lambda x: x[sorting_key])
    files = sorted(files, key=lambda x: x[sorting_key])
    curr_db = sorted(curr_db, key=lambda x: x[sorting_key])

    if reverse_order:
        dirs = dirs[::-1]
        files = files[::-1]
        curr_db = curr_db[::-1]
    
    dirs.extend(files)
    if sorting_key in ["Name", "Ext."]:
        write_db = phc.set_db_data(dirs)
    else:
        write_db = phc.set_db_data(curr_db)
    if write_db.error:
        typer.secho(f'Sorting items failed with "{ERRORS[write_db.error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)

    if flag_result.flags["repeat_show"]:
        display_db()

@app.command()
def export(
    user_path: str = typer.Option(None, "--pathname", "-p", help="Specify a path to export files to")
) -> None:
    phc = get_PHC()

    db_result = phc.get_db_data()
    if db_result.error:
        typer.secho(f'Reading flags failed with "{ERRORS[db_result.error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)
    
    db_items = [item["Name"] for item in db_result.data]
    new_dir = user_path if user_path else "ph_export"
    try:
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        else:
            typer.secho("Export folder already exists.", fg=typer.colors.RED,)
            raise typer.Exit(1)
    except IOError:
        typer.secho(f'Creating directory failed with "{ERRORS[PATH_ERROR]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)
    
    try:
        for name in db_items:
            copy2(Path(name), new_dir)
    except IOError:
        typer.secho(f'Exporting items failed with "{ERRORS[EXPORT_ERROR]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return