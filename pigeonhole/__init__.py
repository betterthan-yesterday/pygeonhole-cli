__app_name__ = "pigeonhole"
__version__ = "0.1.0"

(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    FLAGS_READ_ERROR,
    FLAGS_WRITE_ERROR,
    JSON_ERROR,
    DIR_READ_ERROR,
    ID_ERROR,
) = range(10)

ERRORS = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
    DB_READ_ERROR: "database read error",
    DB_WRITE_ERROR: "database write error",
    FLAGS_READ_ERROR: "flags read error",
    FLAGS_WRITE_ERROR: "flags write error",
    DIR_READ_ERROR: "directory read error",
    ID_ERROR: "file id error",
}
