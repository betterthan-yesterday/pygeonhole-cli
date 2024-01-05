# Pigeonhole Model Controller
# import datetime # import is used in format when ITEM_DATA is retrieved
import os
import stat
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from pygeonhole import SUCCESS, DIR_READ_ERROR
from pygeonhole.database import DatabaseHandler, DatabaseData, ITEM_DATA
from pygeonhole.flags import FlagsHandler, FlagsData

class ItemData(NamedTuple):
    item_data: Dict[str, Any]
    error: int

class DirectoryData(NamedTuple):
    dir_data: List
    error: int

class PH_Controller:
    def __init__(self, db_path: Path, flags_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)
        self._flags_handler = FlagsHandler(flags_path)

    def format_item(self, item_name: str) -> ItemData:
        try:
            stats = os.stat(item_name)
        except OSError:
            return ItemData({}, DIR_READ_ERROR)

        curr_items = self.get_db_data()
        if curr_items.error:
            return ItemData({}, curr_items.error)

        curr_item_format = curr_items.data
        curr_item_data = {}
        for key in curr_item_format[0].keys():
            curr_item_data[key] = eval(ITEM_DATA[key])

        if stat.S_ISDIR(stats.st_mode):
            if "Size" in curr_item_data:
                curr_item_data["Size"] = "--"
            if "Ext." in curr_item_data:
                curr_item_data["Ext."] = "--"

        return ItemData(curr_item_data, SUCCESS)

    def get_dir_data(self, dir_path: str = ".") -> DirectoryData:
        flags_result = self.get_flags_data()
        if flags_result.error:
            return DirectoryData([], flags_result.error)
        flags = flags_result.flags

        item_names = []
        try:
            for (dirpath, dirname, filename) in os.walk(dir_path):
                if flags["show_dirs"]:
                    item_names.extend(dirname)
                item_names.extend(filename)
                break
        except OSError:
            return DirectoryData([], DIR_READ_ERROR)
        
        if not flags["show_hidden"]:
            item_names = [item for item in item_names if not item[0] == "."]

        return DirectoryData(item_names, SUCCESS)
    
    def get_db_data(self) -> DatabaseData:
        read_result = self._db_handler.read_db_data()
        return read_result
    
    def set_db_data(self, db_data: List[Dict[str, Any]]) -> DatabaseData:
        write_result = self._db_handler.write_db_data(db_data)
        return write_result
    
    def get_flags_data(self) -> FlagsData:
        read_result = self._flags_handler.read_flags_data()
        return read_result
    
    def set_flags_data(self, flags_data: Dict[str, Any]) -> FlagsData:
        write_result = self._flags_handler.write_flags_data(flags_data)
        return write_result
