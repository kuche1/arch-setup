#! /usr/bin/env python3

# TODO grub timeout

import subprocess
import shlex
import os
import datetime
import tempfile
import shutil

HERE = os.path.dirname(__file__) + '/'
ENVIRONMENT_PATH = '/etc/environment'
MOUSE_ACCEL_PATH = '/usr/share/X11/xorg.conf.d/90-mouse_accel.conf'
MAKEPKG_CONF_PATH = '/etc/makepkg.conf'
VMWARE_PREFERENCES_PATH = os.path.expanduser('~/.vmware/preferences')

def term(cmds:list):
    cmd = shlex.join(cmds)
    subprocess.run(cmd, shell=True, check=True)

def pkg_install(*packages:list[str]):
    assert type(packages) != str
    term(['sudo', 'pacman', '-S', '--needed', '--noconfirm'] + list(packages))

def aur_install(*packages:list[str]): # TODO check if yay or paru, and if not both install
    assert type(packages) != str
    term(['yay', '-S', '--needed', '--noconfirm'] + list(packages))

def sudo_cp(from_, to):
    term(['sudo', 'cp', from_, to])

def sudo_rm(path):
    term(['sudo', 'rm', path])

def get_backup_name(path):
    return path + ' backup ' + str(datetime.datetime.today())

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
        shutil.rmtree(path)

def sudo_replace_file(to_replace, with_):
    sudo_backup_file(to_replace)
    sudo_cp(with_, to_replace)

def replace_folder(to_replace, with_):
    delete_folder(to_replace)
    shutil.copytree(with_, to_replace)

def main():

    # terminal text editor, debugging
    pkg_install('micro', 'xclip')

    # mouse accel
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write('''
Section "InputClass"
        Identifier "Mouse With No Acceleration"
        MatchDriver "libinput"
        MatchIsPointer "yes"
        Option "AccelProfile" "flat"
EndSection
''')
        name = f.name
    sudo_replace_file(MOUSE_ACCEL_PATH, name)

    # compilation threads
    with open(MAKEPKG_CONF_PATH, 'r') as f:
        cont = f.read()
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        toreplace = '\n#MAKEFLAGS="-j2"\n'
        assert cont.count(toreplace) == 1
        cont = cont.replace(toreplace, '\nMAKEFLAGS="-j$(nproc)"\n')
        f.write(cont)
        name = f.name
    sudo_replace_file(MAKEPKG_CONF_PATH, name)

    # shell
    pkg_install('fish')
    term(['chsh', '-s' ,'$(which fish)'])

    # video drivers
    pkg_install('lib32-mesa', 'vulkan-radeon', 'lib32-vulkan-radeon', 'vulkan-icd-loader', 'lib32-vulkan-icd-loader')

    # DE essential
    pkg_install('bspwm', 'sxhkd', 'polybar')

    # polybar fonts
    pkg_install('ttc-iosevka', 'ttf-nerd-fonts-symbols')
    # polybar widgets
    #term(['checkupdates']) # TODO install if missing
    aur_install('checkupdates-aur')

    # sxhkd programs
    pkg_install('wezterm', 'rofi', 'pulsemixer', 'thunar', 'spectacle', 'dunst')

    # bspwm programs
    pkg_install('mate-polkit')
    #sudo pacman -S --needed nitrogen # wallpaper
    #sudo pacman -S --needed picom # compositor

    # move the config files
    for (dir_, fols, fils) in os.walk(HERE + 'config'):
        for fol in fols:
            source = dir_+'/'+fol
            target = os.path.expanduser('~/.config/') + fol
            replace_folder(target, source)
        break

    # unify theme # TODO? append instead of overwrite
    aur_install('qt5-styleplugins')
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write('QT_QPA_PLATFORMTHEME=gtk2\n')
        f.write('QT_STYLE_OVERRIDE=gtk\n')
        name = f.name
    sudo_replace_file(ENVIRONMENT_PATH, name)

    # additional programs
    pkg_install('gnome-calculator') # calculator
    pkg_install('qbittorrent') # torrent client
    aur_install('librewolf-bin') # browser
    pkg_install('vlc') # video player

    # wine deps
    pkg_install(*'wine-staging giflib lib32-giflib libpng lib32-libpng libldap lib32-libldap gnutls lib32-gnutls mpg123 lib32-mpg123 openal lib32-openal v4l-utils lib32-v4l-utils libpulse lib32-libpulse libgpg-error lib32-libgpg-error alsa-plugins lib32-alsa-plugins alsa-lib lib32-alsa-lib libjpeg-turbo lib32-libjpeg-turbo sqlite lib32-sqlite libxcomposite lib32-libxcomposite libxinerama lib32-libgcrypt libgcrypt lib32-libxinerama ncurses lib32-ncurses opencl-icd-loader lib32-opencl-icd-loader libxslt lib32-libxslt libva lib32-libva gtk3 lib32-gtk3 gst-plugins-base-libs lib32-gst-plugins-base-libs vulkan-icd-loader lib32-vulkan-icd-loader'.split(' '))

    # vmware
    aur_install('vmware-workstation')
    term(['sudo', 'modprobe', '-a', 'vmw_vmci', 'vmmon'])
    term(['sudo', 'systemctl', 'start', 'vmware-networks.service'])
    term(['sudo', 'systemctl', 'enable', 'vmware-networks.service'])
    if not os.path.isdir(os.path.dirname(VMWARE_PREFERENCES_PATH)):
        os.makedirs(os.path.dirname(VMWARE_PREFERENCES_PATH))
    if os.path.isfile(VMWARE_PREFERENCES_PATH): mode = 'w'
    else: mode = 'a'
    with open(VMWARE_PREFERENCES_PATH, mode) as f:
        f.write('\nmks.gl.allowBlacklistedDrivers = "TRUE"\n')

if __name__ == '__main__':
    main()
