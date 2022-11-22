#! /usr/bin/env python3

import subprocess
import shlex
import os
import datetime
import tempfile
import shutil
import time
import psutil
import sys

LAPTOP = psutil.sensors_battery() != None
WARNING_SLEEP = 0.5

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

def term_yes(cmds:list): # TODO unused
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

if __name__ == '__main__':
    term_raw('sudo pacman -S --needed base-devel') # creates `makepkg.conf`

    try:
        pkg_purge('firewalld')
    except subprocess.CalledProcessError:
        pass

    # compilation threads
    sudo_replace_string(
        '/etc/makepkg.conf',
        '\n#MAKEFLAGS="-j2"\n',
        '\nMAKEFLAGS="-j$(nproc)"\n'
    )

    if True: # pacman stuff
        conf_file = '/etc/pacman.conf'
     
        # enable 32bit repo
        sudo_replace_string(
            conf_file,
            '\n#[multilib]\n#Include = /etc/pacman.d/mirrorlist\n',
            '\n[multilib]\nInclude = /etc/pacman.d/mirrorlist\n'
        )
        term(['sudo', 'pacman', '-Syuu'])

        # color
        sudo_replace_string(
            conf_file,
            '\n#Color\n',
            '\nColor\n',
        )
        # verbose packages
        sudo_replace_string(
            conf_file,
            '\n#VerbosePkgLists\n',
            '\nVerbosePkgLists\n',
        )
        # parallel download
        sudo_replace_string(
            conf_file,
            '\n#ParallelDownloads = 5\n',
            '\nParallelDownloads = 5\n',
        )
    
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

    sudo_replace_string(
        '/etc/paru.conf',
        '\n#BottomUp\n',
        '\nBottomUp\n'
    )
