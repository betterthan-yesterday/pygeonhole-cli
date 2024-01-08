# pygeonhole-cli

pygeonhole-cli is a convenient python package that can 
list, sort, and customize the contents of the current 
directory and export the display to a new directory 
directly from the command line.

## Usage

### To get help with command-line arguments
```
pygeonhole-cli --help
```

### Initialize pygeonhole-cli databases
```
pygeonhole-cli init
```

### Example output
```
pygeonhole-cli show -d
```
```
/Users/betterthan-yesterday/pygeonhole-cli:

#  | Name                     | Mode       | Last Modified       | Size | Ext.  |
---------------------------------------------------------------------------------
1 | tests/                   | drwxr-xr-x | 2024-01-05 18:19:26 | --   | --    |
2 | pygeonhole/              | drwxr-xr-x | 2024-01-05 18:15:43 | --   | --    |
3 | requirements.txt         | -rw-r--r-- | 2024-01-05 18:11:00 | 61   | .txt  |
4 | pyproject.toml           | -rw-r--r-- | 2024-01-07 22:07:33 | 788  | .toml |
5 | README.md                | -rw-r--r-- | 2024-01-05 18:14:04 | 54   | .md   |
6 | setup.py                 | -rw-r--r-- | 2024-01-07 22:56:50 | 1046 | .py   |
7 | LICENSE.txt              | -rw-r--r-- | 2024-01-07 22:08:00 | 1076 | .txt  |
---------------------------------------------------------------------------------
```

```
pygeonhole-cli sort Name
```
```
/Users/betterthan-yesterday/pygeonhole-cli:

#  | Name                     | Mode       | Last Modified       | Size | Ext.  |
---------------------------------------------------------------------------------
1 | pygeonhole/              | drwxr-xr-x | 2024-01-05 18:15:43 | --   | --    |
2 | tests/                   | drwxr-xr-x | 2024-01-05 18:19:26 | --   | --    |
3 | LICENSE.txt              | -rw-r--r-- | 2024-01-07 22:08:00 | 1076 | .txt  |
4 | README.md                | -rw-r--r-- | 2024-01-05 18:14:04 | 54   | .md   |
5 | pyproject.toml           | -rw-r--r-- | 2024-01-07 22:07:33 | 788  | .toml |
6 | requirements.txt         | -rw-r--r-- | 2024-01-05 18:11:00 | 61   | .txt  |
7 | setup.py                 | -rw-r--r-- | 2024-01-07 22:56:50 | 1046 | .py   |
---------------------------------------------------------------------------------
```

### Disclaimer

It is recommended that you install the package in a local
virtual env.

First, create an env. 
```sh
python3 -m venv env_for_pyhcli
```

activate that env

```sh
source env_for_pyhcli/bin/activate
```

and then pip install.

## Installation

The current stable version of pygeonhole-cli is available on PyPI and
can be installed by running `pip install pygeonhole-cli`.

Other sources:

- PyPI: https://pypi.org/project/pygeonhole-cli/1.0.0/
- GitHub: https://github.com/betterthan-yesterday/pygeonhole-cli

Note: Compatibility with Windows not yet tested.

## Meta

William Pol - polwilliam0@gmail.com

Distributed under the MIT license. See LICENSE for more information.

https://github.com/bettertha-yesterday/
