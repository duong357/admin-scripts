from pathlib import Path
from shutil import copy2

from bash_tools import add_line_to_file, get_bash_profile
from determine_os import determine_os

def run_this_script():
    current_file = Path(__file__)
    redshift_config_file = current_file.with_name('redshift.conf')
    copy2(redshift_config_file, Path.home().joinpath('.config', redshift_config_file.name))
    add_line_to_file(get_bash_profile(), 'redshift-gtk &')

os = determine_os()
if __name__ == '__main__' and os == 'debian':
    run_this_script()
