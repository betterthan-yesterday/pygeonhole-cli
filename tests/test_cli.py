import json
import pytest
from typer.testing import CliRunner

from pigeonhole import (
    SUCCESS,
    __app_name__,
    __version__,
    cli,
    pigeonhole,
)

from tests.test_pigeonhole import dir_result, file_result, hidden_result, mock_dir, mock_flags, mock_db

runner = CliRunner()

def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout
     
@pytest.mark.parametrize("command, expected", [
    (["init"], SUCCESS),
    (["show"], SUCCESS),
    (["show", "-a"], SUCCESS),
    (["show", "-d"], SUCCESS),
    (["show", "-a", "-d"], SUCCESS),
])
def test_commands(command, expected):
    result = runner.invoke(cli.app, command) 
    assert result.exit_code == expected