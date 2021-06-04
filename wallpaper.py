import re
from itertools import chain
from pathlib import Path
from shutil import copyfile, rmtree, copytree
from subprocess import run
from sys import version_info
from uuid import uuid4

from bash_tools import find
from constants import DATA_DRIVE_PATH
from rename_images_and_videos import file_string_format, rename_stuff, image_formats

MAX_UUID_NAME_LENGTH = 12

dirtypes = ['square', 'vertical', 'horizontal']


def dynamically_import():
    things_to_import = ", ".join(['Image', 'UnidentifiedImageError'])
    exec(f'from PIL import {things_to_import}', globals())


def get_right_dirtype(dirtype: str, images_to: Path = Path.home().joinpath('Pictures')) -> Path:
    assert dirtype in dirtypes
    return images_to.joinpath(f"wallpapers-{dirtype}")


def copy_wallpapers_to_pictures_directory(images_from: Path, images_to: Path):
    assert images_from.is_dir()
    if not images_to.exists():
        images_to.mkdir(exist_ok=True)

    for dirtype in dirtypes:
        get_right_dirtype(dirtype).mkdir(exist_ok=True)

    # This program assumes that the filesystem that holds images_from has unique file names per directory. While path names are relative, thanks to pathlib, two files like tea.jpg and milk/tea.jpg are distinct. existing_image_names should contain unique file names in this sense.
    images_to_copy = []
    existing_image_names = []
    for format in image_formats:
        format = file_string_format(format)
        images_to_copy += list(find(images_from, file_type='f', name_filter=format, case_sensitive=False))
        existing_image_names += [image for image in chain(images_from.iterdir(), images_to.iterdir()) if
                                 re.match(format, image.name, re.IGNORECASE)]
    temp = set(existing_image_names)
    assert len(temp) == len(existing_image_names)
    existing_image_names = temp

    # The following for loop generates a unique name for each image
    for image in images_to_copy:
        while True:
            file_name = f'{str(uuid4())[:MAX_UUID_NAME_LENGTH]}'
            file_name.rstrip('.')
            full_file_name = Path(file_name).with_suffix(image.suffix)
            if full_file_name not in existing_image_names:
                existing_image_names.add(full_file_name)
                break
        # Technically the .name is not necessary since full_file_name is a relative path. If it becomes an absolute path, then you need .name.
        for dirtype in dirtypes:
            exec(
                f"if is_{dirtype}_image(image):copyfile(image, get_right_dirtype(dirtype).joinpath(str(full_file_name.name)))")
        # copyfile(image, images_to.joinpath(str(full_file_name.name)))
    for dirtype in dirtypes:
        image_dir = get_right_dirtype(dirtype)
        remove_small_images(image_dir)
        run(['fdupes', '-dN', str(image_dir)], capture_output=True)
        rename_stuff(image_dir)


def remove_small_images(image_dir: Path, vertical_tolerance: int = 500, horizontal_tolreance: int = 500):
    dynamically_import()
    for image in image_dir.iterdir():
        try:
            width, height = Image.open(image).size
            if width < horizontal_tolreance or height < vertical_tolerance:
                image.unlink()
        except UnidentifiedImageError:
            image.unlink()


def is_horizontal_image(image: Path) -> bool:
    dynamically_import()
    try:
        width, height = Image.open(image).size
        return width > height
    except UnidentifiedImageError:
        return False


def is_vertical_image(image: Path) -> bool:
    dynamically_import()
    try:
        width, height = Image.open(image).size
        return width < height
    except UnidentifiedImageError:
        return False


def is_square_image(image: Path, pixel_tolerance=0) -> bool:
    dynamically_import()
    try:
        width, height = Image.open(image).size
        return abs(width - height) <= pixel_tolerance
    except UnidentifiedImageError:
        return False


def remove_images_from_dir(image_dir: Path, remove_vertical=False, remove_horizontal=False, remove_square=False):
    dynamically_import()
    for image in image_dir.iterdir():
        try:
            if (remove_vertical and is_vertical_image(image)) or (remove_horizontal and is_horizontal_image(image)) or (
                    remove_square and is_square_image(image)):
                image.unlink()
        except UnidentifiedImageError:
            image.unlink()


def run_this_script():
    current_dir = Path(__file__).resolve().parent
    venv_path = current_dir.joinpath('venv')
    if not venv_path.is_dir():
        # Beware when deleting venv while running using python interpreter from it; so far, no undefined behavior happened.
        # rmtree(venv_path)
        run(['python3', '-m', 'venv', venv_path])
        # run(f'python3 -m venv {venv_path}', shell=True)
    assert venv_path.is_dir()
    venv_bin_dir = venv_path.joinpath('bin')
    run(['bash', '-c', f'source {venv_bin_dir.joinpath("activate")}'])
    # run(f"bash -c 'source {venv_bin_dir.joinpath('activate')}'", shell=True)
    run([f'{venv_bin_dir.joinpath("pip3")}', 'install', '--user', 'Pillow'])
    # run(f'{venv_bin_dir.joinpath("pip3")} install Pillow', shell=True)
    #        from PIL import Image, UnidentifiedImageError
    #        global Image, UnidentifiedImageError
    dynamically_import()
    subdirs = ['deviantart', 'reddit'] + [f'wallpapers/{dir}' for dir in
                                          ['amd', 'nix', 'transportation', 'windows-10']]

    picture_dir = Path.home().joinpath('Pictures')
    for dir in subdirs:
        copy_wallpapers_to_pictures_directory(
            Path(__file__).parent.parent.joinpath('photos', 'do-not-automatically-rename', dir),
            picture_dir)
    copy_wallpapers_to_pictures_directory(Path.home().joinpath(DATA_DRIVE_PATH, 'photos', 'numbered'), picture_dir)
    python3_version = version_info[:2]
    assert python3_version[0] == 3
    run(['deactivate'])


if __name__ == '__main__':
    run_this_script()
