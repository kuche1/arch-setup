#! /usr/bin/env bash

i3status | while :
do
	read line
	keyboard="$(xkblayout-state print \"%s\")"
	keyboard="${keyboard:1:-1}"
	echo "$line | $keyboard"
done
