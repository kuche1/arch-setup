#! /usr/bin/env python3

import subprocess
import shlex

def term(cmds:list):
    cmd = shlex.join(cmds)
    subprocess.run(cmd, shell=True, check=True)

def install_packages(packages):
    term(['yay', '-S', '--needed'] + packages)

def main():
    install_packages(['bspwm', 'sxhkd', 'polybar', 'ttc-iosevka', 'ttf-nerd-fonts-symbols',
        'checkupdates-aur', 'wezterm', 'rofi', 'pulsemixer', 'thunar', 'spectacle',
        'dunst', 'mate-polkit'])

if __name__ == '__main__':
    main()
