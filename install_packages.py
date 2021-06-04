from copy import deepcopy
from subprocess import run, CalledProcessError, check_output

from bash_tools import add_line_to_file
from determine_os import *

optional_packages = set('k3b kile okteta kanagram kdiff3 tmux')

common_packages = \
    {
        'ark',
        'audacity',
        'bash-completion',
        'blkid',
        'bovo',
        'chromium',
        'diamond',
        'dolphin',
        'dosbox',
        'easytag',
        'elisa',
        'fdupes',
        'fish',
        'FlightGear',
        'gcc',
        'gimp',
        'git',
        'git',
        'gnubg',
        'gnucash',
        'gnugo',
        'gnuradio',
        'gnushogi',
        'granatier',
        'gwenview',
        'inkscape',
        'juk',
        'kajongg',
        'kalzium',
        'kapman',
        'kate',
        'kblocks',
        'kcalc',
        'kcolorchooser',
        'kdevelop',
        'kgoldrunner',
        'kigo',
        'kmines',
        'knights',
        'kolourpaint',
        'konsole',
        'konversation',
        'kpat',
        'krename',
        'kreversi',
        'krusader',
        'kstars',
        'ksudoku',
        'kwrite',
        'libreoffice',
        'marble',
        'nmap',
        'octave',
        'okteta',
        'okular',
        'openconnect',
        'performous',
        'prename',
        'rsync',
        'screen',
        'scribus',
        'sshfs',
        'supertux',
        'texstudio',
        'tree',
        'valgrind',
        'vim',
        'vlc',
        'wget',
        'xboard',
        'xdg-desktop-portal',
        'xdg-desktop-portal-kde',
        'xkill',
        'xterm',
        'yakuake',
        'zsh'
    }


class OS():
    def __init__(self, package_type: str, install_fail_exit_code=None):
        self.package_type = package_type
        self.packages_to_install = common_packages.copy()
        self.preinstall_commands = []
        self.postinstall_commands = []
        self.install_command = ''
        self.install_fail_exit_code = install_fail_exit_code


#    def get_install_command(self)->str:
#        return f'{self.install_command} {" ".join(sorted(self.packages_to_install))}'

def install_packages(operating_system: OS):
    for command in operating_system.preinstall_commands:
        run(command.split())
    # The following loop installs every package one by one, rather than altogether as one command. For example, `apt install A`, `apt install B`, etc... instead of `apt install A B`
    # Ubuntu will stop installing if you try to install a package that doesn't exist. There seems to be, as of this writing, no option to skip missing packages.
    # This is likely a safety feature to ensure that a package's dependencies exist.
    # Therefore, this script has to try a "brute force" approach.
    failed_packages = []
    for package in operating_system.packages_to_install:
        try:
            command = operating_system.install_command.split()
            command.append(package)
            run(command, check=operating_system.install_fail_exit_code)
            # run(f'{operating_system.install_command} {package}', shell=True, check=operating_system.install_fail_exit_code)
        except CalledProcessError:
            failed_packages.append(package)
    for command in operating_system.postinstall_commands:
        run(command.split())
    if operating_system.install_fail_exit_code:
        print(f"Packages that failed to install: {' '.join(sorted(failed_packages))}")


# def print_commands(operating_system: OS):
#    NUMBER_OF_PACKAGES_TO_PRINT = 3
#    install_commands = [f'{operating_system.install_command} {package}' for package in
#                        operating_system.packages_to_install]
#    for command in operating_system.preinstall_commands + install_commands[:NUMBER_OF_PACKAGES_TO_PRINT]:
#        print(command)
#    if len(install_commands) > NUMBER_OF_PACKAGES_TO_PRINT:
#        print('\n...\n')
#    for command in operating_system.postinstall_commands:
#        print(command)

# for system in operating_systems:
#    exec(f'{system} = OS({"system"})')

def run_this_script():
    os = determine_os()
    assert os in operating_systems
    os = eval(os)
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--tentative', help='print commands that would be executed', dest='tentative',
                        action='store_true')
    args = parser.parse_args()
    #    if args.tentative:
    #        print_commands(os)
    #    else:
    install_packages(os)


debian = OS('deb')
debian.package_type = 'deb'
debian.install_command = 'apt-get install -y'
debian.postinstall_commands += [f'apt-get {command} -y' for command in ['upgrade', 'clean', 'autoclean', 'autoremove']]

ubuntu = deepcopy(debian)
ubuntu.preinstall_commands += ['add-apt-repository -y \'ppa:obsproject/obs-studio\'', 'apt-get update -y',
                               'apt-get remove -y apport']

debian_python_modules = {f'python3-{module}' for module in {'pip', 'venv', 'pil'}}
debian.packages_to_install |= {'redshift', 'texlive-full', 'g++', 'redshift-gtk', 'python3-venv', 'openssh-client',
                               'openssh-server', 'sshfs'}
debian.packages_to_install |= debian_python_modules
ubuntu.packages_to_install |= {'chromium-browser', 'ffmpeg', 'gnome-tweak-tool', 'obs-studio'}
debian.packages_to_install.remove('xkill')
ubuntu.packages_to_install.remove('chromium')

leap = OS('rpm', 104)
leap.install_command = 'zypper in -y'
leap.packages_to_install |= {'texlive-scheme-full', 'imagewriter', 'gcc-c++'}
leap.preinstall_commands += (['zypper rm -y PackageKit', 'wget https://dl.google.com/linux/linux_signing_key.pub',
                              'rpm --import linux_signing_key.pub', 'rm linux_signing_key.pub'])
tumbleweed = deepcopy(leap)
leap.postinstall_commands.append('zypper up -y')
tumbleweed.preinstall_commands = [
                                     "zypper addrepo -cfp 90 'https://ftp.gwdg.de/pub/linux/misc/packman/suse/openSUSE_Tumbleweed/' packman",
                                     "zypper ref", "zypper dist-upgrade --from packman --allow-vendor-change -y",
                                     "zypper install -y --from packman ffmpeg gstreamer-plugins-{good,bad,ugly,libav} libavcodec-full vlc-codecs"] + tumbleweed.preinstall_commands
tumbleweed.postinstall_commands.append('zypper dup -y')

fedora = OS('rpm')
fedora.install_command = 'dnf install -y'
fedora.packages_to_install |= {'kcm-wacomtablet', 'smc', 'smc-music', 'texlive-scheme-full', 'vim-enhanced',
                               '@kde-desktop',
                               'elisa-player'}
fedora.packages_to_install.remove('elisa')
fedora_version = check_output(['rpm', '-E', r'%fedora']).decode('utf-8')
fedora.preinstall_commands.append(
    fr'dnf install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-{fedora_version}.noarch.rpm https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{fedora_version}.noarch.rpm')
fedora.postinstall_commands += [r'dnf remove -y calligra*', 'dnf update -y']

for os in {debian, ubuntu, leap, tumbleweed, fedora}:
    assert os.package_type
    assert os.install_command
    assert len(os.postinstall_commands) > 0

if __name__ == '__main__':
    run_this_script()
