#! /usr/bin/env bash

#uptime | awk '{s=""; for(i=8; i<=NF; ++i) s=s $i; print s}'
#uptime | awk -F 'load average: ' '{print $2}'
#uptime | awk -F 'load average: ' '{print $2}' | awk '{s=""; for(i=1; i<=NF; ++i) s=s $i; print s}'
uptime | awk -F 'load average: ' '{print $2}' | awk '{s=""; for(i=1; i<=NF; ++i) s=s $i; print s}' | tr ',' ' '
