from getpass import getuser
from pathlib import Path

from bash_tools import add_line_to_file
from determine_os import determine_os

# This file is separate from common_setup.py because you can also edit the systemwide vimrc

vim_commands = ['set ai tabstop=4 shiftwidth=4 expandtab', 'syntax on']

os = determine_os()
if os == 'ubuntu':
    system_vimrc = Path('/etc').joinpath('vim', 'vimrc')
    personal_vimrc = Path.home().joinpath('.vimrc')
elif os in {'fedora', 'debian', 'tumbleweed'}:
    system_vimrc = Path('/etc/vimrc')
    personal_vimrc = Path.home().joinpath('.vimrc')
else:
    system_vimrc = None
    personal_vimrc = None


def add_lines_to_system_vimrc(vimrc_file: Path = system_vimrc):
    assert getuser() == 'root'  # not really necessary
    add_lines_to_personal_vimrc(vimrc_file)


def add_lines_to_personal_vimrc(vimrc_file: Path = personal_vimrc):
    for line in vim_commands:
        add_line_to_file(vimrc_file, line)


if __name__ == '__main__':
    exec('add_lines_to_{}_vimrc()'.format('system' if getuser() == 'root' else 'personal'))
