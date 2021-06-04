#!/usr/bin/env python3
from pathlib import Path
from subprocess import run
from typing import Iterable
import constants

from rename_images_and_videos import rename_stuff

NUMBER_OF_PASSPORTS = 3


def determine_drive_order() -> list:
    from determine_os import determine_drive_folder
    drive_dir = determine_drive_folder()
    mount_dir = Path.home().joinpath(constants.DATA_DRIVE_PATH)
    cascading_drives = [mount_dir]
    for i, drive in enumerate(cascading_drives):
        cascading_drives[i] = mount_dir.joinpath(drive)
    for i in range(NUMBER_OF_PASSPORTS):
        drive_name = f'Passport{i + 1}'
        drive = mount_dir.joinpath(drive_name)
        # Drive should not be mounted in two places at the same time
        cascading_drives.append(drive if drive.is_dir() else drive_dir.joinpath(drive_name))

    assert len(cascading_drives) == len(set(cascading_drives))

    for drive in cascading_drives.copy():
        if not drive.is_dir():
            cascading_drives.remove(drive)

    return cascading_drives


rsync_arg = ['rsync']
rsync_options = ['-aztl', '--no-owner', '--no-group', '--progress']
rsync_common_arguments = rsync_arg + rsync_options


# Use this block if run(..., shell=True). Convert it to a string.
# with open(Path.home().joinpath('.bashrc')) as bashrc_file:
#        rsync_common_arguments = rsync_arg + [] if re.search(r'alias.*?rsync\s*=', bashrc_file.read(), flags=re.MULTILINE) else rsync_options

def rsync_two_dirs(source: Path, dest: Path, delete=True):
    run(rsync_common_arguments + (['--delete'] if delete else []) + [f'{source}/', f'{dest}/'])


def rsync_files(sources: Iterable, dest: Path):
    run(rsync_common_arguments + [f'{source}'.rstrip('/') for source in sources] + [f'{dest}/'])


def sync_drives(reverse_sync: bool = False):
    cascading_drives = determine_drive_order()
    if not reverse_sync:
        assert cascading_drives
        rename_stuff(cascading_drives[0].joinpath('photos', 'numbered'))
        print(cascading_drives)
        if len(cascading_drives) <= 1:
            raise EnvironmentError("No other drives exist for file synchronization!")
        for drive in cascading_drives:
            video_dir = drive.joinpath('videos')
            if video_dir.is_dir():
                rename_stuff(video_dir)
                break
        for count, drive in enumerate(cascading_drives[:-1]):
            next_drive = cascading_drives[count + 1]
            for dir in [d for d in drive.iterdir() if not d.name.startswith('.') and d.is_dir()]:
                rsync_two_dirs(dir, next_drive.joinpath(dir.name))
            for file in [f for f in drive.iterdir() if not f.name.startswith('.') and f.is_file()]:
                rsync_files([file], next_drive)
    else:
        cascading_drives.reverse()
        for count, drive in enumerate(cascading_drives[:-1]):
            for dir in [d for d in drive.iterdir() if not d.name.startswith('.') and d.is_dir()]:
                check_if_this_exists = cascading_drives[count + 1].parent.joinpath(dir.name)
                if check_if_this_exists.is_dir():
                    rsync_two_dirs(dir, check_if_this_exists)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Sync drives')
    parser.add_argument('--reverse', dest='reverse_sync', action='store_true')
    args = parser.parse_args()
    sync_drives(args.reverse_sync)
