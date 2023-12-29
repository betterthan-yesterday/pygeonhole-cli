from pathlib import Path
from typing import Optional

import typer

from pigeonhole import (
    ERRORS, __app_name__, __version__, config, database, pigeonhole
)

app = typer.Typer()

def get_PHC() -> pigeonhole.PH_Controller:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho('Config file not found. Please run "pigeonhole init"', fg=typer.colors.RED)
        raise typer.Exit(1)
    if db_path.exists():
        return pigeonhole.PH_Controller(db_path)
    else:
        typer.secho('Database not found. Please run "pigeonhole init"', fg=typer.colors.RED)
        raise typer.Exit(1)
    
def display_files() -> None:
    # Format table
    if len(filenames) == 0 and len(dirnames) == 0:
        typer.secho("There are no items in the directory", fg=typer.colors.RED)
        raise typer.Exit()
    
    maxlen_id = len(str(len(dirnames)+len(filenames)))
    maxlen_filename = len(max(filenames, key=len)) if len(filenames) != 0 else 0
    maxlen_dirname = len(max(dirnames, key=len)) if len(dirnames) != 0 else 0
    maxleng_name = max([maxlen_filename, maxlen_dirname])

    columns = (
        "#",
        "Name",
        "Last Modified",
        "Size",
        # "| Kind  "
    )
    header = f"{columns[0]:<{maxlen_id}}  |"\
             f" {columns[1]:<{maxleng_name}}  |"\
             f" {columns[2]:<0}  |"
    
    typer.secho(f'\n{database.CWD_PATH}:\n', fg=typer.colors.BLUE, bold=True)
    typer.secho(header, fg=typer.colors.BLUE, bold=True)
    typer.secho("-" * len(header), fg=typer.colors.BLUE)

    for id, name in enumerate(dirnames, 1):
        line = f"{id:<{maxlen_id}}  |"\
               f" {name+'/':<{maxleng_name}}  |"\
               f" {(len(columns[2]) - len(str()) - 2) * ' '}  "
        typer.secho(line, fg=typer.colors.BLUE)
        
    for id, name in enumerate(filenames, 1):
        line = f"{id+len(dirnames):<{maxlen_id}}  |"\
               f" {name:<{maxleng_name}}  |"\
               f" {(len(columns[2]) - len(str()) - 2) * ' '}  "
        typer.secho(line, fg=typer.colors.BLUE)

    typer.secho("-" * len(header) + "\n", fg=typer.colors.BLUE)
    
@app.command()
def init() -> None:
    db_path = database.DEFAULT_DB_PATH

    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(f'Creating config file failed with "{ERRORS[app_init_error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)
    
    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(f'Creating database file failed with "{ERRORS[db_init_error]}"', fg=typer.colors.RED,)
        raise typer.Exit(1)
    
    typer.secho(f"The pigeonhole database is {db_path}", fg=typer.colors.GREEN)

    # Input files into database
    phc = get_PHC()

    dir_result = phc.get_dir_data(".")
    if dir_result.error:
        typer.secho(f'Initialization failed with "{ERRORS[dir_result.error]}"', fg=typer.colors.RED)
        raise typer.Exit(1)

    filenames =  [f for f in dir_result.dir_data[0] if not f[0] == "."] # Remove hidden files
    formatted_files = []
    for file in filenames:
        format_result = phc.format_file(file)
        if format_result.error:
            typer.secho(f'Initialization failed with "{ERRORS[format_result.error]}"', fg=typer.colors.RED)
            raise typer.Exit(1)
        formatted_files.append(format_result.file_data)

    write_result = phc.set_db_data(formatted_files)
    if write_result.error:
        typer.secho(f'Initialization failed with "{ERRORS[write_result.error]}"', fg=typer.colors.RED)
        raise typer.Exit(1)

    # display_files()

@app.command()
def list(
    show_all_files: bool = typer.Option(False, "-a", help="Show hidden files"),
    show_dirs: bool = typer.Option(False, "-d", help="Show folders")
) -> None:
    display_files()


@app.command()
def sort() -> None:
    list(False, False)

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