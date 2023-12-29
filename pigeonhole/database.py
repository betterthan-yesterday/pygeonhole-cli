import configparser
import json
from pathlib import Path
from os import getcwd
from typing import Any, Dict, List, NamedTuple

from pigeonhole import DB_READ_ERROR, DB_WRITE_ERROR, JSON_ERROR, SUCCESS, DISPLAY_FLAGS

CWD_PATH = getcwd()
CWD_NAME = CWD_PATH.split("/")[-1]
DEFAULT_DB_PATH = "." + CWD_NAME + "_pigeonhole.json"

def get_database_path(config_file: Path) -> Path:
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])

def init_database(db_path: Path) -> int:
    try:
        with db_path.open("w") as db:
            json.dump(DISPLAY_FLAGS, db, indent=4)
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR
    
class DBResponse(NamedTuple):
    display_flag: Dict[str, bool]
    error: int

class DatabaseHandler:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
    
    def read_todos(self) -> DBResponse:
        try: 
            with self._db_path.open("r") as db:
                try:
                    return DBResponse(json.load(db), SUCCESS)
                except json.JSONDecodeError:
                    return DBResponse([], JSON_ERROR)
        except OSError:
            return DBResponse([], DB_READ_ERROR)
        
    def write_todos(self, display_flag: Dict[str, Any]) -> DBResponse:
        try:
            with self._db_path.open("w") as db:
                json.dump(display_flag, db, indent=4)
            return DBResponse(display_flag, SUCCESS)
        except OSError:
            return DBResponse(display_flag, DB_WRITE_ERROR)