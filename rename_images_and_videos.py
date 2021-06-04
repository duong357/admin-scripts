#!/usr/bin/env python3
import re
import sys
from math import floor, log10
from pathlib import Path
from shutil import move, rmtree
from uuid import uuid4

IMG_PREFIX = 'ARP'
VID_PREFIX = 'ARV'

image_formats = ['jpg', 'png']
video_formats = ['mkv', 'avi', 'mov', 'mp4', 'mts']


def file_string_format(extension: str = None) -> str:
    jpeg_extension = r'\.jpe?g'
    if not extension or re.match(jpeg_extension, extension, flags=re.IGNORECASE):
        return jpeg_extension
    return fr'[^.].*{extension}'


def int_to_digits(n: int) -> int:
    return floor(log10(n)) + 1


def is_good_dir(directory: Path) -> bool:
    def check_single_format(format: str, prefix: str) -> bool:
        format = format.strip().upper()
        prefix = prefix.strip().upper()
        files_to_check = [file for file in sorted(directory.iterdir()) if
                          file.is_file() and re.match(file_string_format(format), file.name, flags=re.IGNORECASE)]
        total_number_of_files_to_check = len(files_to_check)
        for i in range(1, total_number_of_files_to_check + 1):
            check_if_this_file_exists = directory.joinpath(
                f'{prefix}_{i:0{int_to_digits(total_number_of_files_to_check)}}.{format}')
            if not check_if_this_file_exists.is_file():
                print(f'{directory.resolve()} is a bad directory and needs to be renamed')
                return False
        return True

    for format in image_formats:
        if not check_single_format(format, prefix=IMG_PREFIX):
            return False
    for format in video_formats:
        if not check_single_format(format, prefix=VID_PREFIX):
            return False
    return True


def rename_stuff(directory: Path):
    if directory.name.strip().lower() == 'no-rename':
        return
    for file in [f for f in directory.iterdir() if f.is_file()]:
        if re.match(file_string_format(), file.suffix, flags=re.IGNORECASE):
            file.replace(file.with_suffix('.JPG'))
    if not is_good_dir(directory):
        temp_dir = Path.home().joinpath(str(uuid4()))
        temp_dir.mkdir()

        def rename_single_format(format: str, prefix: str):
            format = format.strip().upper()
            prefix = prefix.strip().upper()
            count = 1
            files = [f for f in sorted(directory.iterdir()) if
                     f.is_file() and re.match(file_string_format(format), f.name, flags=re.IGNORECASE)]
            total_number_of_files = len(files)
            for file in files:
                temp = f'{prefix}_{count:0{int_to_digits(total_number_of_files)}}.{format}'
                move(file, temp_dir.joinpath(temp))
                count += 1

        for format in image_formats:
            rename_single_format(format, IMG_PREFIX)
        for format in video_formats:
            rename_single_format(format, VID_PREFIX)
        for file in temp_dir.iterdir():
            move(file, directory.joinpath(file.name))
        rmtree(temp_dir)
    for file in [f for f in sorted(directory.iterdir()) if not f.name.startswith('.') and f.is_dir()]:
        rename_stuff(file)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        raise EnvironmentError('No input arguments!')
    for arg in sys.argv[1:]:
        arg = Path(arg)
        if arg.is_dir():
            rename_stuff(arg)
