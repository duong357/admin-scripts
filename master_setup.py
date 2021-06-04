import re
import os
from getpass import getuser

import common_setup, install_packages
from pathlib import Path
from shutil import rmtree
from subprocess import run, check_output, CalledProcessError

import constants
from bash_tools import add_line_to_file


# Run this script as root
def add_drive_to_fstab(label: str, mount_point: Path):
    encoding = 'utf-8'
    try:
        data_dev_command = check_output(['blkid', '-L', label])
        data_uuid_command = check_output(['blkid', data_dev_command.decode(encoding).strip()])
    except CalledProcessError:
        return

    data_uuid_data = data_uuid_command.decode(encoding).strip()
    data_uuid_match = re.search(r'(?<!PART)UUID="(.*?)"', data_uuid_data)
    data_fs_match = re.search(r'(?<!\w)TYPE="(.*?)"', data_uuid_data)

    data_uuid, data_fs = data_uuid_match.group(1), data_fs_match.group(1)
    add_line_to_file(Path('/etc/fstab'),
                     f"UUID={data_uuid}\t{mount_point}\t{data_fs}\tdefaults,auto,nofail\t0\t2")

    run(['systemctl', 'daemon-reload'])


def run_this_script():
    who_ran_this_script, uid = '', ''
    try:
        who_ran_this_script = os.environ['SUDO_USER']
        uid = os.environ['SUDO_UID']
    except KeyError:
        print('Run this script with sudo!')
        exit(1)
    assert who_ran_this_script and uid

    install_packages.run_this_script()

    data_mount_point = Path('/').joinpath('home', who_ran_this_script, constants.DATA_DRIVE_PATH)
    add_line_to_file(Path('/etc/hosts'), 'XXX.XXX.XXX.XXX\some-host')
    add_drive_to_fstab(constants.DATA_DRIVE_PATH, data_mount_point)

    # rmtree(Path(__file__).parent.joinpath('venv'))
    # common_setup.run_this_script()


if __name__ == '__main__':
    run_this_script()
