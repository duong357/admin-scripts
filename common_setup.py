# RUN FROM PASSPORT
# MAKE SURE FIREFOX DOES NOT RUN WHILE THIS SCRIPT RUNS
# What this script does is subject to changes in file organization, particularly NFS
import os
import re
import tarfile
from subprocess import run

from pathlib import Path
from shutil import rmtree
from zipfile import ZipFile

import setup_sshfs
import setup_redshift
from bash_tools import add_line_to_file, find, get_bash_profile
from sync import rsync_files
from update_vim import add_lines_to_personal_vimrc


def run_this_script():
    # TODO: Use argparse to suppress output

    # Add some commands to .bashrc
    bash_aliases = \
        {
            'ls': 'ls -l',
            'la': 'ls -dal .*',
            '..': 'cd ..',
            '...': 'cd ../..',
            'wget': 'wget -np -rkp -l 30',
            'rsync': 'rsync -avzl --progress ' + ' '.join([f'--no-{option}' for option in ['owner', 'group']])
        }
    alias_string_buf = []
    for key in bash_aliases:
        alias_string_buf.append(f"{key}='{bash_aliases[key]}'")
    bash_aliases = ' '.join(alias_string_buf)
    bashrc_commands = ['unset SSH_ASKPASS', 'set -o vi', fr"alias {bash_aliases}"]
    for command in bashrc_commands:
        add_line_to_file(Path.home().joinpath('.bashrc'), command)

    # Add some stuff to .profile
    bash_profile = get_bash_profile()
    desktop_session_var = os.environ.get('DESKTOP_SESSION')
    if desktop_session_var:
        desktop_session_path = Path(desktop_session_var)
        if desktop_session_path.name.strip().lower() == 'plasma':
            add_line_to_file(bash_profile, 'export GTK_USE_PORTAL=1')
    add_line_to_file(bash_profile, 'yakuake &')

    add_lines_to_personal_vimrc()

    drive_dir = Path(__file__).resolve().parent.parent

    # Create ~/bin if it doesn't already exist; some systems automatically add ~/bin to PATH if ~/bin exists
    bin_dir = Path.home().joinpath('bin')
    if bin_dir.is_file() or not bin_dir.is_dir():
        bin_dir.mkdir()
    try:
        Path.home().joinpath('Desktop', 'bin').symlink_to(bin_dir)
    except FileExistsError:
        pass
    env_path = os.environ.get('PATH', None)
    path_var_set = {Path(path) for path in env_path.split(':')}
    if bin_dir not in path_var_set:
        os.environ['PATH'] = str(bin_dir) if not env_path else f'{env_path}:{bin_dir}'

    # Disable Firefox's prompt that asks whether to open or save file
    firefox_prefs_files = list(find(Path.home(), name_filter='prefs.js', file_type='f', case_sensitive=True))
    for file in firefox_prefs_files:
        add_line_to_file(file, r'user_pref("browser.download.forbid_open_with", true);')

    # Copy apps and archives to Downloads folder
    application_dir = drive_dir.joinpath('software', 'applications', 'linux', 'amd64')
    downloads_dir = Path.home().joinpath('Downloads')
    dirs_to_link = ['archives', 'apps']
    for dir in dirs_to_link:
        try:
            Path.home().joinpath('Desktop', dir).symlink_to(downloads_dir.joinpath(dir))
        except FileExistsError:
            pass
    # Do not add the usual --delete flag here
    rsync_files([application_dir.joinpath(dir) for dir in dirs_to_link], downloads_dir)

    ## TODO: copy packages to archive directory
    #
    # Extract all non-package (package ~= deb/rpm/...) archives
    archives_dir = Path.home().joinpath('Downloads', 'archives')
    for file in archives_dir.glob('*.zip'):
        with ZipFile(file) as zip_file:
            zip_file.extractall(path=archives_dir)
    for file in [f for f in archives_dir.iterdir() if
                 re.match('[^.].*\.(?:bz(?:ip)2|[gx]z)', f.name, flags=re.IGNORECASE)]:
        suffix = file.suffix.lstrip('.')
        with tarfile.open(file, f'r:{"bz2" if suffix == "bzip2" else suffix}') as my_tar_file:
            my_tar_file.extractall(path=archives_dir)

    # Create symlinks to the copied apps and archives
    for program in {'Discord/Discord', 'Telegram/Telegram',
                    'thunderbird/thunderbird'}:  # | set(get_full_file_name_from_prefix('jdk', archives_dir).joinpath('bin').glob('*.java{,c}')):
        executable = archives_dir.joinpath(program)
        try:
            bin_dir.joinpath(executable.name).symlink_to(executable)
        except (FileExistsError, FileNotFoundError):
            pass

    appimage_dir = Path.home().joinpath('Downloads', 'apps')
    for file in appimage_dir.rglob('.*'):
        file.unlink() if file.is_file() else rmtree(file)
    for file in appimage_dir.iterdir():
        file.chmod(0o755)

    git_info = {'name': 'Heinz Jung', 'email': 'some-email@something.com'}
    for key in git_info:
        run(['git', 'config', '--global', f'user.{key}', git_info[key]])

    setup_sshfs.run_this_script()
    setup_redshift.run_this_script()


if __name__ == '__main__':
    run_this_script()
