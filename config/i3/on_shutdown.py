#! /usr/bin/env python3

import i3ipc
import subprocess
import shlex
import os

shitdown_script_path = os.path.expanduser('~/.config/i3/destroy-virtual-sinks-for-audio-sharing.sh')

def on_shutdown(conn):
    subprocess.run(shlex.join([shitdown_script_path]), shell=True)

conn = i3ipc.Connection()
conn.on('ipc_shutdown', on_shutdown)
conn.main()
