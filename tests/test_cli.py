import json
import pytest
from typer.testing import CliRunner

from pygeonhole import (
    SUCCESS,
    __app_name__,
    __version__,
    cli,
    pygeonhole,
)

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
    (["show", "-d", "-a"], SUCCESS),
    (["sort", "Name"], SUCCESS),
    (["sort", "Name", "-r"], SUCCESS),
    (["sort", "Mode"], SUCCESS),
    (["sort", "Mode", "-r"], SUCCESS),
    (["sort", "Last Modified"], SUCCESS),
    (["sort", "Last Modified", "-r"], SUCCESS),
    (["sort", "Size"], SUCCESS),
    (["sort", "Size", "-r"], SUCCESS),
    (["sort", "Ext."], SUCCESS),
    (["sort", "Ext.", "-r"], SUCCESS),
])
def test_commands(command, expected):
    result = runner.invoke(cli.app, command) 
    assert result.exit_code == expected