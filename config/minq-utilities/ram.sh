#! /usr/bin/env bash

free -h | head -n 2 | tail -1 | awk '{print $7}'
