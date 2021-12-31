#! /usr/bin/env python3

import subprocess
import shlex
import os
import datetime
import tempfile

HERE == os.path.dirname(__file__) + '/'
ENVIRONMENT_PATH = '/etc/environment'

def term(cmds:list):
    cmd = shlex.join(cmds)
    subprocess.run(cmd, shell=True, check=True)

def pkg_install(*packages:list[str]):
    term(['sudo', 'pacman', '-S', '--needed'] + packages)

def aur_install(*packages:list[str]): # TODO check if yay or paru, and if not both install
    term(['yay', '-S', '--needed'] + packages)

def backup_folder(path):
    if os.path.isdir(path):
        newname = path + ' backup ' + datetime.datetime.today()\
        newname = get_backup_name(path)
        shutil.move(path, newname)

def sudo_backup_file(path):
    newname = get_backup_name(path)
    term(['sudo', 'mv', path, newname])

def main():

    # essential
    pkg_install('bspwm', 'sxhkd', 'polybar')

    # polybar fonts
    pkg_install('ttc-iosevka', 'ttf-nerd-fonts-symbols')
    # polybar widgets
    term('checkupdates') # TODO install if missing
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
            backup_folder(target)
            shutil.rmtree(target)
            shutil.copytree(source, target)
        break

    # unify theme
    sudo_backup_file(ENVIRONMENT_PATH)
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write('QT_QPA_PLATFORMTHEME=gtk2\n')
        f.write('QT_STYLE_OVERRIDE=gtk\n')
        name = f.name
    sudo_move(name, ENVIRONMENT_PATH)

    # additional cool programs
    pkg_install('gnome-calculator')
    pkg_install('qbittorrent')
    # TODO vmware

if __name__ == '__main__':
    main()
