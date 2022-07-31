#! /usr/bin/env python3

#sudo iptables -A INPUT -s 188.165.207.20 -j DROP

import os
import subprocess
import shlex

HERE = os.path.dirname(os.path.realpath(__file__))
IP_BANS_FILE = os.path.join(HERE, 'ips-to-ban')

with open(IP_BANS_FILE, 'r') as f:
    cont = f.read()

for ip in cont.splitlines():
    comment_char = '#'
    if comment_char in ip:
        ind = ip.index(comment_char)
        ip = ip[:ind]
    ip = ip.strip()
    if ip == '':
        continue

    print(f'Blocking IP: {ip}')
    subprocess.run(shlex.join(['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP']), shell=True, check=True)

print('Done')
