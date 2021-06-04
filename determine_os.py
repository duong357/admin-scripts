import argparse
import platform
from getpass import getuser
from pathlib import Path
import re

operating_systems = ['fedora', 'tumbleweed', 'leap', 'ubuntu', 'debian']

os_file_path = Path('/etc/os-release')
assert os_file_path.is_file()
def determine_os() -> str:
    with open(os_file_path, 'r') as os_release_file:
        for line in os_release_file:
            for os in operating_systems:
                if re.search(os.strip(), line, flags=re.IGNORECASE):
                    return os
    raise EnvironmentError("Cannot determine OS")

def determine_drive_folder()->Path:
    os = determine_os()
    drive_folder = Path('media').joinpath(getuser())
    if not (re.match('debian', os) or re.match('ubuntu', os)):
        drive_folder = Path('/run').joinpath(drive_folder)
    else:
        drive_folder = Path(Path('/').root).joinpath(drive_folder)
    return drive_folder


if __name__ == '__main__':
#   parser = argparse.ArgumentParser()
#   parser.add_argument('-d', help='determine OS', dest='det_os', action='store_true')
#   parser.add_argument('-c', help='common packages for all distros', dest='compaks', action='store_true')
#   args = parser.parse_args()
#   if args.det_os:
    print(determine_os())
