__app_name__ = "pigeonhole"
__version__ = "0.1.0"

(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    DIR_READ_ERROR,
    ID_ERROR,
) = range(8)

ERRORS = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
    DB_READ_ERROR: "database read error",
    DB_WRITE_ERROR: "database write error",
    DIR_READ_ERROR: "directory read error",
    ID_ERROR: "file id error",
}

DISPLAY_FLAGS = {
    "SHOW_HIDDEN_FILES": False,
    "SHOW_DIRS": False
}