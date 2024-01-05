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
    EXPORT_ERROR,
    PATH_ERROR,
) = range(11)

ERRORS = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
    DB_READ_ERROR: "database read error",
    DB_WRITE_ERROR: "database write error",
    FLAGS_READ_ERROR: "flags read error",
    FLAGS_WRITE_ERROR: "flags write error",
    DIR_READ_ERROR: "directory read error",
    EXPORT_ERROR: "export items error",
    PATH_ERROR: "unidentified path error",
    JSON_ERROR: "json format error"
}
