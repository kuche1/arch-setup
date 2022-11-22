#! /usr/bin/env python3

from run_pre_install import *

if __name__ == '__main__':
    term_raw('sudo chsh -s $(which fish) $USER')

    pkg_install('openssh') # TODO check for alternative ?
    if not (os.path.isfile(os.path.expanduser('~/.ssh/id_rsa')) or os.path.isfile(os.path.expanduser('~/.ssh/id_rsa.pub'))):
        term(['ssh-keygen', '-f', os.path.expanduser('~/.ssh/id_rsa'), '-N', ''])
    with open(os.path.expanduser('~/.ssh/config'), 'a') as f:
        f.write('\nForwardX11 yes\n')

    # https://dandavison.github.io/delta/get-started.html
    term(['git', 'config', '--global', 'core.pager', 'delta'])
    term(['git', 'config', '--global', 'interactive.diffFilter', 'delta --color-only'])
    term(['git', 'config', '--global', 'delta.navigate', 'true'])
    term(['git', 'config', '--global', 'merge.conflictstyle', 'diff3'])
    term(['git', 'config', '--global', 'diff.colorMoved', 'default'])

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
    sudo_replace_file('/etc/environment', name)

    sudo_replace_string(
        '/usr/share/applications/steam.desktop',
        '\nExec=/usr/bin/steam-runtime %U\n',
        '\nExec=/usr/bin/steam-runtime -silent -nochatui -nofriendsui %U\n',
    )
    
    sudo_replace_string(
        '/usr/share/applications/discord.desktop',
        '\nExec=/usr/bin/discord\n',
        '\nExec=/usr/bin/discord --disable-smooth-scrolling\n',
    )

    sudo_replace_string(
        '/usr/share/applications/guilded.desktop',
        '\nExec=/opt/Guilded/guilded %U\n',
        '\nExec=/opt/Guilded/guilded --disable-smooth-scrolling %U\n',
    )

    if not LAPTOP:
        service_start_and_enable(f'syncthing@{USERNAME}')
    
    # power manager
    if LAPTOP:
        pkg_force_install('tlp')
        sudo_replace_string('/etc/tlp.conf',
            '\n#STOP_CHARGE_TRESH_BAT0=80\n',
            '\nSTOP_CHARGE_TRESH_BAT0=1\n',)
        service_start_and_enable('tlp')

    sudo_replace_string(
        '/etc/lightdm/lightdm.conf',
        '\n#autologin-user=\n',
       f'\nautologin-user={USERNAME}\n',
    )
    service_enable('lightdm')

    if True: # boot options
        try:
            term(['update-grub', '--version'])
        except subprocess.CalledProcessError:
            aur_install('update-grub')

        conf_file = '/etc/default/grub'

        sudo_replace_string(
            conf_file,
            '\nGRUB_TIMEOUT=5\n',
            '\nGRUB_TIMEOUT=1\n',
        )
        sudo_replace_string(
            conf_file,# TODO fix if not the first item
            '\nGRUB_CMDLINE_LINUX_DEFAULT="quiet ',
            '\nGRUB_CMDLINE_LINUX_DEFAULT="noquiet ',
        )
        term(['sudo', 'update-grub'])

    # vmware
    # if not LAPTOP:
    #     if not os.path.isdir(VMWARE_VMS_PATH):
    #         os.makedirs(VMWARE_VMS_PATH)
    #     if is_btrfs(VMWARE_VMS_PATH):
    #         term(['chattr', '-R', '+C', VMWARE_VMS_PATH])
    #         #term(['chattr', '+C', VMWARE_VMS_PATH])
    #     aur_install('vmware-workstation')
    #     term(['sudo', 'modprobe', '-a', 'vmw_vmci', 'vmmon'])
    #     service_start_and_enable('vmware-networks')
    #     if not os.path.isdir(os.path.dirname(VMWARE_PREFERENCES_PATH)):
    #         os.makedirs(os.path.dirname(VMWARE_PREFERENCES_PATH))
    #     if os.path.isfile(VMWARE_PREFERENCES_PATH): mode = 'w'
    #     else: mode = 'a'
    #     with open(VMWARE_PREFERENCES_PATH, mode) as f: # TODO check if exists first
    #         f.write('\nmks.gl.allowBlacklistedDrivers = "TRUE"\n')

    # kernel
    # pkg_install('linux-zen', 'linux-zen-headers') # TODO provide alternative kernel ? xmonad
    # term(['sudo', 'update-grub'])

    term(['sync'])