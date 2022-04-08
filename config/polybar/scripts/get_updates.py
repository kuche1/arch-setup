#! /usr/bin/env python3

import subprocess

upd = aur = 0

try:
    upd = subprocess.check_output('checkupdates').count(b'\n')
except subprocess.CalledProcessError:
    upd = 0

try:
    aur = subprocess.check_output(['paru', '-Qua']).count(b'\n')
except subprocess.CalledProcessError:
    aur = 0

print(f'{upd}|{aur} ')
