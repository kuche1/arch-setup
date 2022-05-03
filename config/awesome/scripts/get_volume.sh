#! /usr/bin/env bash

amixer sget Master | grep 'Front Left:' | cut -d ' ' -f 7 | cut -b 2- | sed 's/.$//'
