#! /usr/bin/env python3

import subprocess
import shlex
import os
import datetime

HERE == os.path.dirname(__file__) + '/'

def term(cmds:list):
    cmd = shlex.join(cmds)
    subprocess.run(cmd, shell=True, check=True)

def pkg_install(*packages:list[str]):
    term(['sudo', 'pacman', '-S', '--needed'] + packages)

def aur_install(*packages:list[str]): # TODO check if yay or paru, and if not both install
    term(['yay', '-S', '--needed'] + packages)

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
            if os.path.isdir(target):
                newname = fol + ' backup ' + datetime.datetime.today()
                shutil.movetree(target, newname)
            shutil.copytree(source, target)
        break

if __name__ == '__main__':
    main()
