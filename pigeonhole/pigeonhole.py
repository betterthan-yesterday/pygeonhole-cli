# Pigeonhole Model Controller
import datetime
from os import walk, stat
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from pigeonhole import SUCCESS, DIR_READ_ERROR
from pigeonhole.database import DatabaseHandler, DatabaseData

class FileData(NamedTuple):
    file_data: Dict[str, Any]
    error: int

class DirectoryData(NamedTuple):
    dir_data: List[List]
    error: int

class PH_Controller:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def format_file(self, filename: str) -> FileData:
        try:
            stats = stat(filename)
        except OSError:
            return FileData({}, DIR_READ_ERROR)

        file = {
            "Name": filename,
            "Last Modified": str(datetime.datetime.fromtimestamp(stats.st_ctime))[:-7],
            "Size": stats.st_size,
        }
        return FileData(file, SUCCESS)

    def get_dir_data(self, dir_path: Path) -> DirectoryData:
        filenames = []
        dirnames = []
        try:
            for (dirpath, dirname, filename) in walk(dir_path):
                filenames.extend(filename)
                dirnames.extend(dirname)
                break
        except OSError:
            return DirectoryData([], DIR_READ_ERROR)

        return DirectoryData([filenames, dirnames], SUCCESS)
    
    def get_db_data(self) -> DatabaseData:
        read_result = self._db_handler.read_db_data()
        return read_result
    
    def set_db_data(self, db_data: List[Dict[str, Any]]) -> DatabaseData:
        write_result = self._db_handler.write_db_data(db_data)
        return write_result


    # def add(self, description: List[str], priority: int=2) -> CurrentTodo:
    #     description_text = " ".join (description)
    #     if not description_text.endswith("."):
    #         description_text += "."
    #     todo = {
    #         "Description": description_text,
    #         "Priority": priority,
    #         "Done": False,
    #     }
    #     read = self._db_handler.read_todos()
    #     if read.error == DB_READ_ERROR:
    #         return CurrentTodo(todo, read.error)
    #     read.todo_list.append(todo)
    #     write = self._db_handler.write_todos(read.todo_list)
    #     return CurrentTodo(todo, write.error)
    
    # def get_todo_list(self) -> List[Dict[str, Any]]:
    #     read = self._db_handler.read_todos()
    #     return read.todo_list
    
    # def set_done(self, todo_id: int) -> CurrentTodo:
    #     read = self._db_handler.read_todos()
    #     if read.error:
    #         return CurrentTodo({}, read.error)
        
    #     try:
    #         todo = read.todo_list[todo_id - 1]
    #     except IndexError:
    #         return CurrentTodo({}, ID_ERROR)
        
    #     todo["Done"] = True
    #     write = self._db_handler.write_todos(read.todo_list)
    #     return CurrentTodo(todo, write.error)
    
    # def remove(self, todo_id: int) -> CurrentTodo:
    #     read = self._db_handler.read_todos()
    #     if read.error:
    #         return CurrentTodo({}, read.error)
        
    #     try:
    #         todo = read.todo_list.pop(todo_id - 1)
    #     except IndexError:
    #         return CurrentTodo({}, ID_ERROR)
        
    #     write = self._db_handler.write_todos(read.todo_list)
    #     return CurrentTodo(todo, write.error)
    
    # def clear(self) -> CurrentTodo:
    #     write = self._db_handler.write_todos([])
    #     return CurrentTodo({}, write.error)