import configparser
import json
from pathlib import Path
from os import getcwd
from typing import Any, Dict, List, NamedTuple

from pigeonhole import DB_READ_ERROR, DB_WRITE_ERROR, JSON_ERROR, SUCCESS

ITEM_DATA = {
    "Name": "item_name",
    "Last Modified": "str(datetime.datetime.fromtimestamp(stats.st_ctime))[:-7]",
    "Size": "str(stats.st_size)",
    "Extension": "os.path.splitext(item_name)[1]"
}

CWD_PATH = getcwd()
CWD_NAME = CWD_PATH.split("/")[-1]
DEFAULT_DB_PATH = "." + CWD_NAME + "_ph.json"

def get_database_path(config_file: Path) -> Path:
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])

def init_database(db_path: Path) -> int:
    try:
        db_path.write_text("[]")
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR
    
class DatabaseData(NamedTuple):
    data: List[Dict[str, any]]
    error: int

class DatabaseHandler:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
    
    def read_db_data(self) -> DatabaseData:
        try: 
            with self._db_path.open("r") as db:
                try:
                    return DatabaseData(json.load(db), SUCCESS)
                except json.JSONDecodeError:
                    return DatabaseData([], JSON_ERROR)
        except OSError:
            return DatabaseData([], DB_READ_ERROR)
        
    def write_db_data(self, data: List[Dict[str, Any]]) -> DatabaseData:
        try:
            with self._db_path.open("w") as db:
                json.dump(data, db, indent=4)
            return DatabaseData(data, SUCCESS)
        except OSError:
            return DatabaseData(data, DB_WRITE_ERROR)