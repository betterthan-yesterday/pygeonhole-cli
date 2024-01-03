import json
import pytest
import os
from typer.testing import CliRunner

from pigeonhole import (
    DB_READ_ERROR,
    SUCCESS,
    __app_name__,
    __version__,
    cli,
    pigeonhole,
)

dir_result = {
    "Name": "testing",
    "Mode": "drwxr-xr-x",
    "Size": "--",
    "Ext.": "--"
}

file_result = {
    "Name": "test.txt",
    "Mode": "-rw-r--r--",
    "Size": "11",
    "Ext.": ".txt"
}

hidden_result = {
    "Name": ".hidden_test",
    "Mode": "-rw-r--r--",
    "Size": "19",
    "Ext.": ""
}

@pytest.fixture
def mock_dir(tmp_path):
    file = tmp_path / "test.txt"
    with file.open("w", encoding ="utf-8") as f:
        f.write("Hello World")
    hidden_file = tmp_path / ".hidden_test"
    with hidden_file.open("w", encoding ="utf-8") as f:
        f.write("This file is hidden")
    return tmp_path

@pytest.fixture
def mock_db(tmp_path):
    dir = tmp_path / "testing"
    dir.mkdir(parents=True, exist_ok=True)
    db_file = dir / ".ph.json"
    return db_file

@pytest.fixture
def mock_flags(tmp_path):
    flags_file = tmp_path / "testing" / ".ph_flags.json"
    return flags_file

# Test Controller functions

"""
format_item() will be hard to test as it calls os.stat() which calls inside the
working cwd and not the system under test. Will have to research more on Mock.
"""
# def test_format(mock_db, mock_flags, mock_dir):
#     phc = pigeonhole.PH_Controller(mock_db, mock_flags)
#     dir_result = phc.get_dir_data(mock_dir)
#     db_result = phc.get_db_data()
#     print(dir_result.dir_data)
#     format_result = phc.format_item("test.txt")
#     assert format_result.error == 0
#     assert format_result.item_data == db_result.data[1]

@pytest.mark.parametrize("flags, expected", [
    ({"show_hidden": False, "show_dirs": False}, ["test.txt"]),
    ({"show_hidden": False, "show_dirs": True}, ["testing", "test.txt"]),
    ({"show_hidden": True, "show_dirs": False}, ["test.txt", ".hidden_test"]),
    ({"show_hidden": True, "show_dirs": True}, ["testing", "test.txt", ".hidden_test"]),
])
def test_get_dir(mock_db, mock_flags, mock_dir, flags, expected):
    with mock_flags.open("w") as db:
        json.dump(flags, db, indent=4)

    phc = pigeonhole.PH_Controller(mock_db, mock_flags)
    dir_result = phc.get_dir_data(mock_dir)
    print(dir_result.dir_data)
    assert dir_result.error == 0
    assert dir_result.dir_data == expected

@pytest.mark.parametrize("databases", [
    [file_result],
    [dir_result, file_result],
    [file_result, hidden_result],
    [dir_result, file_result, hidden_result],
])
def test_get_db(mock_db, mock_flags, databases):
    with mock_db.open("w") as db:
        json.dump(databases, db, indent=4)

    phc = pigeonhole.PH_Controller(mock_db, mock_flags)
    db_result = phc.get_db_data()
    print(db_result.data)
    assert db_result.error == 0
    assert db_result.data == databases

@pytest.mark.parametrize("flags", [
    {"show_hidden": False, "show_dirs": False},
    {"show_hidden": False, "show_dirs": True},
    {"show_hidden": True, "show_dirs": False},
    {"show_hidden": True, "show_dirs": True},
])
def test_get_flags(mock_db, mock_flags, flags):
    with mock_flags.open("w") as db:
        json.dump(flags, db, indent=4)

    phc = pigeonhole.PH_Controller(mock_db, mock_flags)
    flags_result = phc.get_flags_data()
    print(flags_result.flags)
    assert flags_result.error == 0
    assert flags_result.flags == flags

@pytest.mark.parametrize("databases", [
    [file_result],
    [dir_result, file_result],
    [file_result, hidden_result],
    [dir_result, file_result, hidden_result],
])
def test_set_db(mock_db, mock_flags, databases):
    phc = pigeonhole.PH_Controller(mock_db, mock_flags)
    write_result = phc.set_db_data(databases)
    assert write_result.error == 0
    read_result = phc.get_db_data()
    assert read_result.data == databases

@pytest.mark.parametrize("flags", [
    {"show_hidden": False, "show_dirs": False},
    {"show_hidden": False, "show_dirs": True},
    {"show_hidden": True, "show_dirs": False},
    {"show_hidden": True, "show_dirs": True},
])
def test_set_flags(mock_db, mock_flags, flags):
    phc = pigeonhole.PH_Controller(mock_db, mock_flags)
    write_result = phc.set_flags_data(flags)
    assert write_result.error == 0
    read_result = phc.get_flags_data()
    assert read_result.flags == flags
