#! /usr/bin/env bash

# mpstat | tail -1 | awk '{print $7}'

requested_time="$1"

mpstat "$requested_time" 1 | tail -1 | awk '{print $6}'
