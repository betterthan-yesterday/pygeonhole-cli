import configparser
import json
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from pigeonhole import FLAGS_READ_ERROR, FLAGS_WRITE_ERROR, JSON_ERROR, SUCCESS
from pigeonhole.database import CWD_NAME

FLAGS = {
    "show_hidden": False,
    "show_dir": False,
}

DEFAULT_FLAGS_PATH = "." + CWD_NAME + "_ph_flags.json"

def get_flags_path(config_file: Path) -> Path:
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["flags"])

def init_flags(flags_path: Path) -> int:
    try:
        with flags_path.open("w") as flags:
            json.dump(FLAGS, flags, indent=4)
        return SUCCESS
    except OSError:
        return FLAGS_WRITE_ERROR
    
class FlagsData(NamedTuple):
    flags: Dict[str, bool]
    error: int

class FlagsHandler:
    def __init__(self, flags_path: Path) -> None:
        self._flags_path = flags_path
    
    def read_flags_data(self) -> FlagsData:
        try: 
            with self._flags_path.open("r") as flags:
                try:
                    return FlagsData(json.load(flags), SUCCESS)
                except json.JSONDecodeError:
                    return FlagsData([], JSON_ERROR)
        except OSError:
            return FlagsData([], FLAGS_READ_ERROR)
        
    def write_flags_data(self, data: Dict[str, Any]) -> FlagsData:
        try:
            with self._flags_path.open("w") as flags:
                json.dump(data, flags, indent=4)
            return FlagsData(data, SUCCESS)
        except OSError:
            return FlagsData(data, FLAGS_WRITE_ERROR)