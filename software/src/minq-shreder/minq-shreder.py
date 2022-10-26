#! /usr/bin/env python3

# TODO this can be optimized
# running a single thread is causes IO bottleneck, so it might be best to use only 1 thread
# ^^^^^^^ this might turn out to be false

import argparse
import os
import subprocess
import threading

PASSES = 16

def shred_file(file, quick=False):
    if quick:
        modes = ['-v']
    else:
        modes = ['-v'] * PASSES + ['-zu']
    for mode in modes:
        subprocess.run(['shred', mode, '-n1', file], check=True)
        subprocess.run(['sync'], check=True)

def main(folder):
    for d, _, fils in os.walk(folder):
        paths = [os.path.join(d, fil) for fil in fils]
        for fil in paths:
            shred_file(fil, quick=True)
        for fil in paths:
            shred_file(fil)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Secure folder deletion tool')
    parser.add_argument('folder', help='Folder to delete')
    args = parser.parse_args()

    main(args.folder)
