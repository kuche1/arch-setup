#! /usr/bin/env bash

df -h / | tail -1 | awk '{print $4}'
