import re
from typing import Iterable
from pathlib import Path


def grep(pattern: str, files: Iterable, case_sensitive=True) -> dict:
    new_dict = {}
    for file in files:
        if file.is_dir():
            new_dict |= grep(pattern, file.iterdir(), case_sensitive=case_sensitive)
        with open(file, 'r') as f:
            text = f.read()
            flags = re.MULTILINE
            if case_sensitive:
                flags = flags | re.IGNORECASE
            matches = re.findall(pattern, text, flags=flags)
            if matches and file not in new_dict.keys():
                new_dict[file] = set()
            for match in matches:
                new_dict[file].add(match)
    return new_dict


def find(path: Path, name_filter: str = None, file_type: str = None, case_sensitive: bool = True):
    args = locals().copy()
    for arg in args:
        if isinstance(args[arg], str):
            exec(f'{arg} = {arg}.strip().lower()')
    for file in path.expanduser().rglob('*'):
        if name_filter:
            match = re.fullmatch(name_filter, file.name, flags=0 if case_sensitive else re.IGNORECASE)
            if not match:
                continue
        if file_type:
            file_type = file_type.strip()
            if file_type == 'f' and file.is_file():
                pass
            elif file_type == 'd' and file.is_dir():
                pass
            else:
                continue
        yield file


def add_line_to_file(file_path: Path, line: str):
    '''TODO: make sure ^ and $ surround line'''
    '''Surely a more elegant way to write this function exists.'''
    with open(file_path, 'a+') as file:
        try:
            match = grep(line, [file_path])
        except FileNotFoundError:
            file.write(f'{line}\n')
            return
        if not match.keys():
            file.write(f'{line}\n')


def directory_is_empty(dir: Path):
    return list(dir.iterdir())


def get_full_file_name_from_prefix(name: str, directory_to_scan: Path = None) -> Path:
    '''NOTE: Returns only one arbitrary file that fits the name; this function discards all other files'''
    if not directory_to_scan:
        directory_to_scan = Path(__file__)
    name = name.strip().lower()
    for file in directory_to_scan.iterdir():
        if file.name.strip().lower().startswith(name):
            return file
    raise FileNotFoundError(f'No files that begin with [{name}] (no brackets, case insensitive)')


def copy_directory_structure(source_dir: Path, dest_dir: Path):
    assert source_dir.is_dir()
    if not dest_dir.exists():
        dest_dir.mkdir()
    else:
        assert dest_dir.is_dir()
    for file in source_dir.rglob('*'):
        if file.is_dir():
            dest_dir.joinpath(file.relative_to(source_dir)).mkdir(exist_ok=True)


def sed_replace(pattern: str, replacement: str, files: Iterable):
    for file in files:
        try:
            with open(file, 'r+') as some_file:
                buf = re.sub(pattern, replacement, some_file.read(), flags=re.MULTILINE | re.DOTALL)
                some_file.seek(0)
                some_file.write(buf)
        except UnicodeDecodeError:
            continue
            # TODO: raise exceptions here if needed


def get_bash_profile() -> Path:
    bash_profile = Path.home().joinpath('.bash_profile')
    if not bash_profile.is_file:
        bash_profile = bash_profile.with_name('.profile')
    return bash_profile
