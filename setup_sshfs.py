from pathlib import Path
from subprocess import run, DEVNULL

from bash_tools import add_line_to_file, get_bash_profile
from constants import DATA_DRIVE_PATH


def ping(address: str, count: int = 1) -> bool:
    ping_command = run(['ping', '-c', str(count), address], check=True, stdout=DEVNULL)
    return not ping_command.returncode


def run_this_script():
    ssh_dir = Path.home().joinpath('.ssh')
    ssh_dir.mkdir(exist_ok=True)
    ssh_dir.chmod(0o700)
    username, hostname = 'some-host', 'some-host'
    full_host_name = f'{username}@{hostname}'
    run(['ssh-keygen', '-f', ssh_dir.joinpath('id_rsa'), '-t', 'rsa', '-b', '4096'])
    run(['ssh-copy-id', full_host_name])
    user_mount_dir = Path.home().joinpath(DATA_DRIVE_PATH)
    user_mount_dir.mkdir(parents=True, exist_ok=True)
    main_mount_dir = Path(f'/home/{username}').joinpath(DATA_DRIVE_PATH)

    bin_dir = Path.home().joinpath('bin')
    bin_dir.mkdir(exist_ok=True)
    mount_program = bin_dir.joinpath('mount-some-host')
    add_line_to_file(mount_program, r'#!/bin/bash')
    add_line_to_file(mount_program, rf'sshfs {full_host_name}:{main_mount_dir} {user_mount_dir} -o reconnect')
    mount_program.chmod(0o744)

    add_line_to_file(get_bash_profile(), mount_program.name)


if __name__ == '__main__':
    run_this_script()
    # print(ping('www.google.com'))
