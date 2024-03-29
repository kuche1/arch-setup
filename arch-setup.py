#! /usr/bin/env python3

# TODO stop and disable `firewalld.service`

# TODO make all into package/functionality pairs

import subprocess
import shlex
import os
import datetime
import tempfile
import shutil
import time
import psutil
import sys

HERE = os.path.dirname(__file__) + '/'
USERNAME = os.environ.get('USER')
LAPTOP = psutil.sensors_battery() != None

try: REAL_FILE_NAME = os.readlink(__file__)
except OSError: REAL_FILE_NAME = __file__
REAL_FILE_NAME = os.path.basename(REAL_FILE_NAME)

WARNING_SLEEP = 0.2
VMWARE_VMS_PATH = os.path.expanduser('~/data/vmware')
VMWARE_PREFERENCES_PATH = os.path.expanduser('~/.vmware/preferences')
ENVIRONMENT_PATH = '/etc/environment'
GRUB_CONF_PATH = '/etc/default/grub'
MAKEPKG_CONF_PATH = '/etc/makepkg.conf'
PACMAN_CONF_PATH = '/etc/pacman.conf'
PARU_CONF_PATH = '/etc/paru.conf'
LIGHTDM_CONFIG_PATH = '/etc/lightdm/lightdm.conf'
TLP_CONF_PATH = '/etc/tlp.conf'

WMS = []
WMS.append(WM_BSPWM := 'bspwm')
WMS.append(WM_I3 := 'i3')
WM = WM_I3 # let user select WM

INSTALL_VMWARE = False
INSTALL_TIMESHIFT = False

def warning(info:str):
    print('====================')
    print(f'WARNING: {info}')
    print('====================')
    print(f'Continuing as normal in {WARNING_SLEEP} sec')
    print('====================')
    time.sleep(WARNING_SLEEP)

def term_raw(cmd:str):
    assert type(cmd) == str
    print(f'Running: {cmd}')
    subprocess.run(cmd, shell=True, check=True)

def term(cmds:list):
    assert type(cmds) in (list, tuple)
    cmd = shlex.join(cmds)
    term_raw(cmd)

def term_yes(cmds:list):
    assert type(cmds) in (list, tuple)
    cmd = 'yes | ' + shlex.join(cmds)
    term_raw(cmd)

def pkg_force_install(*packages:list[str]):
    assert type(packages) in [list, tuple]
    print(f'Force installing package(s): {packages}')
    term_yes(['sudo', 'pacman', '-S', '--needed'] + list(packages))
    # '--noconfirm'

def pkg_install(*packages:list[str]):
    assert type(packages) in [list, tuple]
    print(f'Installing package(s): {packages}')
    term(['sudo', 'pacman', '-S', '--needed', '--noconfirm'] + list(packages))

def pkg_purge(*packages:list[str]):
    assert type(packages) in [list, tuple]
    print(f'Purging package(s): {packages}')
    term(['sudo', 'pacman', '-Rns', '--noconfirm'] + list(packages))

def aur_install(*packages:list[str]):
    assert type(packages) != str
    tool = 'yay'
    try: term([tool, '--version'])
    except subprocess.CalledProcessError: tool = 'paru'
    term([tool, '--version']) # TODO install 1 of the 2 if this doesn't work
    print(f'Installing AUR package(s): {packages}')
    term([tool, '-S', '--needed', '--noconfirm'] + list(packages))

def service_enable(name:str):
    assert type(name) == str
    term(['sudo', 'systemctl', 'enable', name])

def service_start_and_enable(name:str):
    assert type(name) == str
    term(['sudo', 'systemctl', 'start', name])
    service_enable(name)

def is_btrfs(path:str):
    bestMatch = ''
    fsType = ''
    for part in psutil.disk_partitions():
        if path.startswith(part.mountpoint) and len(bestMatch) < len(part.mountpoint):
            fsType = part.fstype
            bestMatch = part.mountpoint
    return fsType == 'btrfs'

def sudo_cp(from_, to):
    term(['sudo', 'cp', from_, to])

def sudo_rm(path):
    term(['sudo', 'rm', path])

def get_backup_name(path):
    return path + '-backup-' + str(datetime.datetime.today()).replace(' ', '-')

def sudo_backup_file(path):
    assert not os.path.isdir(path)
    if os.path.isfile(path):
        newname = get_backup_name(path)
        sudo_cp(path, newname)

def backup_folder(path):
    assert not os.path.isfile(path)
    if os.path.isdir(path):
        newname = get_backup_name(path)
        shutil.copytree(path, newname)

def sudo_delete_file(path):
    assert not os.path.isdir(path)
    if os.path.isfile(path):
        sudo_backup_file(path)
        sudo_rm(path)

def delete_folder(path):
    assert not os.path.isfile(path)
    if os.path.isdir(path):
        backup_folder(path)
        try: shutil.rmtree(path)
        except OSError: os.remove(path)
        #os.remove(path) #os.unlink()

def sudo_replace_file(to_replace, with_):
    sudo_backup_file(to_replace)
    sudo_cp(with_, to_replace)

def replace_folder(to_replace, with_):
    delete_folder(to_replace)
    shutil.copytree(with_, to_replace)

def sudo_replace_string(file, to_replace, with_):
    with open(file, 'r') as f:
        cont = f.read()
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        match cont.count(to_replace):
            case 0:
                warning(f'Variable in file ({file}) seems to have already been set. This happens when you run this script a second time, or if you change the variable manually. Variable:\n{to_replace}\n')
                return
            case 1:
                pass
            case _:
                warning(f'Variable in file ({file}) found more than one. This is an error.')
                sys.exit(1)
        cont = cont.replace(to_replace, with_)
        f.write(cont)
        name = f.name
    sudo_replace_file(file, name)

def main():

    # DHCP
    pkg_install('dhcpcd')

    # debugging
    pkg_install('micro', 'xclip')

    # shell
    pkg_install('fish')
    term_raw('sudo chsh -s $(which fish) $USER')

    if True: # pacman stuff

        # creates `makepkg.conf`
        pkg_install('base-devel')

        # compilation threads
        sudo_replace_string(MAKEPKG_CONF_PATH,
            '\n#MAKEFLAGS="-j2"\n',
            '\nMAKEFLAGS="-j$(nproc)"\n')

        # 32bit repo
        sudo_replace_string(PACMAN_CONF_PATH,
            '\n#[multilib]\n#Include = /etc/pacman.d/mirrorlist\n',
            '\n[multilib]\nInclude = /etc/pacman.d/mirrorlist\n')
        term(['sudo', 'pacman', '-Syuu'])

        # TODO add chaotic AUR ?

        # color
        sudo_replace_string(PACMAN_CONF_PATH,
            '\n#Color\n',
            '\nColor\n')

        # verbose packages
        sudo_replace_string(PACMAN_CONF_PATH,
            '\n#VerbosePkgLists\n',
            '\nVerbosePkgLists\n')

        # parallel download
        sudo_replace_string(PACMAN_CONF_PATH,
            '\n#ParallelDownloads = 5\n',
            '\nParallelDownloads = 5\n')

        # paru
        try:
            pkg_install('paru')
        except subprocess.CalledProcessError:
            old_cwd = os.getcwd()
            os.chdir('/tmp/')
            if os.path.isdir('./paru'):
                shutil.rmtree('./paru')
            term(['git', 'clone', 'https://aur.archlinux.org/paru.git'])
            os.chdir('./paru')
            term(['makepkg', '-si', '--noconfirm'])
            os.chdir(old_cwd)

        # # install yay if not present
        # try:
        #     term(['yay', '--version'])
        # except subprocess.CalledProcessError:
        #     old_cwd = os.getcwd()
        #     os.chdir('/tmp/')
        #     if os.path.isdir('./yay'):
        #         shutil.rmtree('./yay')
        #     term(['git', 'clone', 'https://aur.archlinux.org/yay.git'])
        #     os.chdir('./yay')
        #     term(['makepkg', '-si', '--noconfirm'])
        #     os.chdir(old_cwd)

        sudo_replace_string(PARU_CONF_PATH,
            '\n#BottomUp\n',
            '\nBottomUp\n')

    # ssh stuff
    pkg_install('openssh') # TODO? check for alternative
    if not (os.path.isfile(os.path.expanduser('~/.ssh/id_rsa')) and os.path.isfile(os.path.expanduser('~/.ssh/id_rsa.pub'))):
        term(['ssh-keygen', '-f', os.path.expanduser('~/.ssh/id_rsa'), '-N', ''])
    with open(os.path.expanduser('~/.ssh/config'), 'a') as f:
        f.write('\nForwardX11 yes\n')

    # git config
    #term(['git', 'config', '--global', 'user.email', 'you@example.com'])
    pkg_install('git-delta')
    # https://dandavison.github.io/delta/get-started.html
    term(['git', 'config', '--global', 'core.pager', 'delta'])
    term(['git', 'config', '--global', 'interactive.diffFilter', 'delta --color-only'])
    term(['git', 'config', '--global', 'delta.navigate', 'true'])
    term(['git', 'config', '--global', 'merge.conflictstyle', 'diff3'])
    term(['git', 'config', '--global', 'diff.colorMoved', 'default'])

    # video drivers
    pkg_install('lib32-mesa', 'vulkan-radeon', 'lib32-vulkan-radeon', 'vulkan-icd-loader', 'lib32-vulkan-icd-loader') # AMD
    pkg_install('lib32-mesa', 'vulkan-intel', 'lib32-vulkan-intel', 'vulkan-icd-loader', 'lib32-vulkan-icd-loader') # intel

    # wine deps
    pkg_install(*'wine-staging giflib lib32-giflib libpng lib32-libpng libldap lib32-libldap gnutls lib32-gnutls mpg123 lib32-mpg123 openal lib32-openal v4l-utils lib32-v4l-utils libpulse lib32-libpulse libgpg-error lib32-libgpg-error alsa-plugins lib32-alsa-plugins alsa-lib lib32-alsa-lib libjpeg-turbo lib32-libjpeg-turbo sqlite lib32-sqlite libxcomposite lib32-libxcomposite libxinerama lib32-libgcrypt libgcrypt lib32-libxinerama ncurses lib32-ncurses opencl-icd-loader lib32-opencl-icd-loader libxslt lib32-libxslt libva lib32-libva gtk3 lib32-gtk3 gst-plugins-base-libs lib32-gst-plugins-base-libs vulkan-icd-loader lib32-vulkan-icd-loader'.split(' '))

    # ok version of java since some apps may require java (ewwww)
    pkg_install('jre11-openjdk')

    # window manager
    if WM == WM_BSPWM:

        # bspwm essentials
        pkg_install('bspwm', 'sxhkd')
        aur_install('polybar')

        # sxhkd dependencies
        pkg_install('thunar') # pkg_install('caja', 'caja-open-terminal') # file manager
        pkg_install('wezterm') # terminal # kitty doesn't always behave over ssh
        pkg_install('rofi', 'pulsemixer', 'spectacle', 'dunst')
        pkg_install('xsecurelock')

        # polybar fonts
        pkg_install('ttc-iosevka', 'ttf-nerd-fonts-symbols')

        # polybar widgets
        pkg_install('pacman-contrib')

        # bspwm dependencies
        pkg_install('mate-polkit') ; pkg_install('gnome-keyring') # might as well also set this up
        pkg_install('dex')
        pkg_install('network-manager-applet')
        #sudo pacman -S --needed nitrogen # wallpaper
        #sudo pacman -S --needed picom # compositor

    elif WM == WM_I3:

        try: pkg_purge('i3')
        except: pass
        pkg_install('i3') # TODO this still fails?

        aur_install('xkblayout-state-git') # keyboard language switcher
        pkg_install('python-psutil') # needed to determine weather laptop or not
        pkg_install('python-i3ipc')
        pkg_install('dex') # autostart
        pkg_install('network-manager-applet')

        pkg_install('xfce4-terminal')

    else:

        raise Exception(f'Unknow WM: {WM}')
   
    # install the softwares # TODO untested
    # TODO tested and it fails
    # for (dir_, fols, fils) in os.walk(os.path.join(HERE, 'software', 'bin')):
    #     for fil in fils:
    #         path = os.path.join(dir_, fil)
    #         os.symlink(path, os.path.join('/usr/bin/', fil)) # TODO will require sudo

    # TODO install services

    # unify theme # we could also install adwaita-qt and adwaita-qt6
        # themes can be found in `/usr/share/themes` (or at lean on ubuntu)
        # docs on xsettings `https://wiki.archlinux.org/title/Xsettingsd`
    #aur_install('adwaita-qt', 'adwaita-qt6')
    pkg_install('adwaita-qt5', 'adwaita-qt6')
    pkg_install('lxappearance-gtk3') # GTK theme control panel
    pkg_install('qt5ct', 'qt6ct') # qt theme control panel
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write('GTK_THEME=Adwaita-dark\n')
        f.write('QT_QPA_PLATFORMTHEME=qt5ct\n')
        f.write('MANGOHUD=1\n')
        f.write('EDITOR=micro\n')
        # f.write('TERMINAL=wezterm\n')
        f.write('BROWSER=librewolf\n')
        f.write('\n')
        # f.write('# linux-xanmod variables\n')
        # f.write('_microarchitecture=15 # zen3\n')
        # f.write('use_numa=n # n==I don\'t have multiple processors\n')
        # f.write('#use_tracers=n # n==limits debugging and analysis of the kernel\n')
        # f.write('#_makenconfig=y # tweak kernel options prior to a build via nconfig\n')
        f.write('\n')
        name = f.name
    sudo_replace_file(ENVIRONMENT_PATH, name)

    # dark theme
    pkg_install('gnome-themes-extra')
    aur_install('paper-icon-theme')

    # terminal utilities
    pkg_install('sysstat') # utilities for system stats
    aur_install('bootiso') # safer dd alternative
    pkg_install('fd') # find alternative
    pkg_install('bat') # cat alternative
    pkg_install('bottom') # system monitor
    pkg_install('tldr') # man alternative
    pkg_install('duf') # better du
    pkg_install('lsd') # better ls
    pkg_install('poppler') # pdf combiner
    pkg_install('pdftk', 'bcprov', 'java-commons-lang') # pdf cutter
    aur_install('pirate-get-git') # torrent browser
    pkg_install('yt-dlp') # video downloader
    pkg_install('htop') # system monitor
    pkg_install('w3m') # web browser
    aur_install('minq-xvideos-git') # xvideos browser
    aur_install('minq-nhentai-git', 'python-minq-caching-thing-git') # nhentai browser
    pkg_install('trash-cli') # trash manager
    pkg_install('streamlink') # enables watching streams (examples: yt, twitch)
    aur_install('ani-cli-git') # anime watcher

    # terminal
    pkg_install('xfce4-terminal') # wezterm is gay # kitty doesn't always behave over ssh
    # menu
    pkg_install('rofi')
    # screenshooter
    pkg_install('spectacle')
    # polkit
    pkg_install('mate-polkit') # pkg_install('gnome-keyring')

    # additional programs
    aur_install('mangohud-common', 'mangohud', 'lib32-mangohud') # gayming overlay
    #aur_install('freezer-appimage') # music # commented due to slow download
    aur_install('nuclear-player-bin') # music
    aur_install('mcomix-git') # .cbr file reader (manga) (Junji Ito)
    pkg_install('gnome-disk-utility')
    pkg_install('baobab') # disk usage anal
    pkg_install('gparted') # btrfs partition resize
    pkg_install('ark') # archive manager
    if INSTALL_TIMESHIFT: aur_install('timeshift') # backup
    pkg_install('miniupnpc'); pkg_install('transmission-gtk') # aur_install('transmission-sequential-gtk')
        # torrent client # qbittorrent causes PC to lag, also has a weird bug where it refuses to download torrents
    pkg_install('tigervnc') # vnc
    pkg_install('lutris')
    pkg_install('ksysguard') # task manager
    pkg_install('songrec') # find a song by sample
    aur_install('vscodium-bin') # IDE
    aur_install('rustdesk-bin') # remote desktop

    # file manager
    pkg_install('thunar', 'thunar-archive-plugin', 'gvfs') # pkg_install('caja', 'caja-open-terminal')
    tmp = 'thunar.desktop'
    term(['xdg-mime', 'default',  tmp, 'inode/directory'])

    # video player
    pkg_install('mpv') # pkg_install('vlc')
    #tmp = 'mpv.desktop' # tmp = 'vlc.desktop' # TODO see the real name of `mpv.desktop`
    # # video
    # term('xdg-mime default vlc.desktop video/x-flv'.split(' '))
    # term('xdg-mime default vlc.desktop video/x-msvideo'.split(' '))
    # term('xdg-mime default vlc.desktop video/x-matroska'.split(' '))
    # term('xdg-mime default vlc.desktop video/mp4'.split(' '))
    # term('xdg-mime default vlc.desktop video/quicktime'.split(' '))
    # term('xdg-mime default vlc.desktop video/mpeg'.split(' '))
    # # audio
    # term('xdg-mime default vlc.desktop audio/mpeg'.split(' '))
    # term('xdg-mime default vlc.desktop audio/x-wav'.split(' '))

    pkg_install('nomacs') # image viewer
    term('xdg-mime default org.nomacs.ImageLounge.desktop image/gif'.split(' '))
    term('xdg-mime default org.nomacs.ImageLounge.desktop image/png'.split(' '))
    term('xdg-mime default org.nomacs.ImageLounge.desktop image/jpeg'.split(' '))
    term('xdg-mime default org.nomacs.ImageLounge.desktop image/webp'.split(' '))

    pkg_install('steam')
    sudo_replace_string('/usr/share/applications/steam.desktop',
        '\nExec=/usr/bin/steam-runtime %U\n',
        '\nExec=/usr/bin/steam-runtime -silent -nochatui -nofriendsui %U\n')
    pkg_install('lib32-libappindicator-gtk2') # makes it so that the taskbar menu follows the system theme

    # TODO fuck this cancer shit
    pkg_install('discord')
    sudo_replace_string('/usr/share/applications/discord.desktop',
        '\nExec=/usr/bin/discord\n',
        '\nExec=/usr/bin/discord --disable-smooth-scrolling\n')

    try:
        aur_install('guilded')
    except:
        warning('the current guilded maintainer is an idiot, and so guilded will not be installed')
    else:
        sudo_replace_string('/usr/share/applications/guilded.desktop',
            '\nExec=/opt/Guilded/guilded %U\n',
            '\nExec=/opt/Guilded/guilded --disable-smooth-scrolling %U\n')

    aur_install('librewolf-bin') # browser
    term(['unset', 'BROWSER', '&&', 'xdg-settings', 'set', 'default-web-browser', 'librewolf.desktop'])

    pkg_install('syncthing')
    if not LAPTOP:
        service_start_and_enable(f'syncthing@{USERNAME}')

    # power manager
    if LAPTOP:
        pkg_force_install('tlp')
        sudo_replace_string(TLP_CONF_PATH,
            '\n#STOP_CHARGE_TRESH_BAT0=80\n',
            '\nSTOP_CHARGE_TRESH_BAT0=1\n',)
        service_start_and_enable('tlp')

    # vmware
    if (not LAPTOP) and INSTALL_VMWARE:
        if not os.path.isdir(VMWARE_VMS_PATH):
            os.makedirs(VMWARE_VMS_PATH)
        if is_btrfs(VMWARE_VMS_PATH):
            term(['chattr', '-R', '+C', VMWARE_VMS_PATH])
            #term(['chattr', '+C', VMWARE_VMS_PATH])
        aur_install('vmware-workstation')
        term(['sudo', 'modprobe', '-a', 'vmw_vmci', 'vmmon'])
        service_start_and_enable('vmware-networks')
        if not os.path.isdir(os.path.dirname(VMWARE_PREFERENCES_PATH)):
            os.makedirs(os.path.dirname(VMWARE_PREFERENCES_PATH))
        if os.path.isfile(VMWARE_PREFERENCES_PATH): mode = 'w'
        else: mode = 'a'
        with open(VMWARE_PREFERENCES_PATH, mode) as f: # TODO check if exists first
            f.write('\nmks.gl.allowBlacklistedDrivers = "TRUE"\n')

    # login manager
    pkg_install('lightdm', 'lightdm-gtk-greeter')
    # unneeded? create group # sudo groupadd -r autologin
    # unneeded? add to autologin # term(['sudo', 'gpasswd', '-a', USERNAME, 'autologin'])
    sudo_replace_string(LIGHTDM_CONFIG_PATH,
        '\n#autologin-user=\n',
       f'\nautologin-user={USERNAME}\n',)
    #sudo_replace_string(LIGHTDM_CONFIG_PATH,
    #    '\n#autologin-session=\n',
    #    '\nautologin-session=bspwm\n',)
    service_enable('lightdm')

    # boot time
    aur_install('update-grub')
    sudo_replace_string(GRUB_CONF_PATH,
        '\nGRUB_TIMEOUT=5\n',
        '\nGRUB_TIMEOUT=1\n')
    sudo_replace_string(GRUB_CONF_PATH,# TODO fix if not the first item
        '\nGRUB_CMDLINE_LINUX_DEFAULT="quiet ',
        '\nGRUB_CMDLINE_LINUX_DEFAULT="noquiet ')
    term(['sudo', 'update-grub'])

    if True: # kernel
        pkg_install('linux-zen', 'linux-zen-headers') # TODO provide alternative kernel ? xmonad
        term(['sudo', 'update-grub'])

    print('Syncing file system...')
    term(['sync'])

if __name__ == '__main__':
    main()
