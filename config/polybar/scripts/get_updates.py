#! /usr/bin/env python3

import subprocess

upd = aur = 0

try:
    upd = subprocess.check_output('checkupdates').count(b'\n')
except subprocess.CalledProcessError:
    pass

try:
    aur = subprocess.check_output('checkupdates-aur').count(b'\n')
except subprocess.CalledProcessError:
    pass

print(f'{upd}|{aur}')
