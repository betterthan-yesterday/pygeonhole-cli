from pathlib import Path
from typing import Optional

import typer

from pigeonhole import (
    ERRORS, __app_name__, __version__, config, database, flags, pigeonhole
)

app = typer.Typer()

def get_PHC() -> pigeonhole.PH_Controller:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
        flags_path = flags.get_flags_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho('Config file not found. Please run "pigeonhole init"', fg=typer.colors.RED)
        raise typer.Exit(1)
    if db_path.exists() and flags_path.exists():
        return pigeonhole.PH_Controller(db_path, flags_path)
    else:
        typer.secho('Database not found. Please run "pigeonhole init"', fg=typer.colors.RED)
        raise typer.Exit(1)

"""
This function essentially resets the program (though it does not reset
the flags) so it is necessary to warn the user of adding and removing
files while in the middle of execution. Probably better to just tell
user to re-init.
"""
def update_db() -> None:
    phc = get_PHC()

    flags_result = phc.get_flags_data()
    if flags_result.error:
        typer.secho(f'Displaying items failed with "{ERRORS[flags_result.error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)

    db_result = phc.get_db_data()
    if db_result.error:
        typer.secho(f'Displaying items failed with "{ERRORS[db_result.error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)

    dir_result = phc.get_dir_data(flags_result.flags["show_hidden"], flags_result.flags["show_dirs"])
    if dir_result.error:
        typer.secho(f'Displaying items failed with "{ERRORS[dir_result.error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)
    
    if len(db_result.data) != len(dir_result.dir_data):
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

    dir_result = phc.get_dir_data(False, False)
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
def format() -> None:
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
    dirs = []
    files = []

    if flag_result.flags["repeat_show"]:
        display_db()

# @app.command()
# def add(
#     description: List[str] = typer.Argument(...),
#     priority: int = typer.Option(2, "--priority", "-p", min=1, max=3),
# ) -> None:
#     todoer = get_todoer()
#     todo, error = todoer.add(description, priority)
#     if error:
#         typer.secho(f'Adding to-do failed with "{ERRORS[error]}"', fg=typer.colors.RED)
#         raise typer.Exit(1)
#     else:
#         typer.secho(f"""to-do: "{todo['Description']}" was added with priority: {priority}""", fg=typer.colors.GREEN)

# @app.command(name="list_todo")
# def list_all() -> None:
#     todoer = get_todoer()
#     todo_list = todoer.get_todo_list()
#     if len(todo_list) == 0:
#         typer.secho("There are no tasks in the to-do list yet", fg=typer.colors.RED)
#         raise typer.Exit()
#     typer.secho("\nto-do list:\n", fg=typer.colors.BLUE, bold=True)
#     columns = (
#         "ID.  ",
#         "| Priority  ",
#         "| Done  ",
#         "| Description  " 
#     )
#     headers = "".join(columns)
#     typer.secho(headers, fg=typer.colors.BLUE, bold=True)
#     typer.secho("-" * len(headers), fg=typer.colors.BLUE)
#     for id, todo in enumerate(todo_list, 1):
#         desc, priority, done = todo.values()
#         font_strikethrough = True if done else False
#         font_colour = typer.colors.BLUE if done else typer.colors.BRIGHT_BLUE
#         typer.secho(
#             f"{id}{(len(columns[0]) - len(str(id))) * ' '}"
#             f"| ({priority}){(len(columns[1]) - len(str(priority)) - 4) * ' '}"
#             f"| {done}{(len(columns[2]) - len(str(done)) - 2) * ' '}"
#             f"| {desc}",
#             fg=font_colour,
#             strikethrough=font_strikethrough
#         )
#     typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE)

# @app.command(name="done")
# def set_done(todo_id: int = typer.Argument(...)) -> None:
#     todoer = get_todoer()
#     todo, error = todoer.set_done(todo_id)
#     if error:
#         typer.secho(f'Completing to-do # "{todo_id}" failed with "{ERRORS[error]}"', fg=typer.colors.RED)
#         raise typer.Exit(1)
#     else:
#         typer.secho(f"""to-do # {todo_id} "{todo['Description']}" completed!""", fg=typer.colors.GREEN)

# @app.command()
# def remove(
#     todo_id: int = typer.Argument(...),
#     force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation.")
# ) -> None:
#     todoer = get_todoer()
    
#     def _remove():
#         todo, error = todoer.remove(todo_id)
#         if error:
#             typer.secho(f'Removing to-do # {todo_id} failed with "{ERRORS[error]}"', fg=typer.colors.RED)
#             raise typer.Exit(1)
#         else:
#             typer.secho( f"""to-do # {todo_id}: '{todo["Dedscription"]}' was removed""", fg=typer.colors.GREEN)
    
#     if force:
#         _remove()
#     else:
#         todo_list = todoer.get_todo_list()
#         try:
#             todo = todo_list[todo_id - 1]
#         except IndexError:
#             typer.secho("Invalid TODO_ID", fg=typer.colors.RED)
#             raise typer.Exit(1)
        
#         delete = typer.confirm(f"Delete to-do # {todo_id}: {todo['Description']}?")
#         if delete:
#             _remove()
#         else:
#             typer.secho("Operation cancelled")

# @app.command()
# def clear(
#     force: bool = typer.Option(
#         ...,
#         prompt="Delete all to-dos?",
#         help="Force deletion without confirmation"
#     )
# ) -> None:
#     todoer = get_todoer()
#     if force:
#         error = todoer.clear().error
#         if error:
#             typer.secho(f'Removing to-dos failed with "{ERRORS[error]}"', fg=typer.colors.RED)
#             raise typer.Exit(1)
#         else:
#             typer.secho("All to-dos were removed", fg=typer.colors.GREEN)
#     else:
#         typer.echo("Operation cancelled")


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