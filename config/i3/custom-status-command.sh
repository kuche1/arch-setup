#! /usr/bin/env bash

HERE="$(dirname $0)"

netspeed_file="$HERE/net-speed.sh"

updates_regular="$(checkupdates | wc -l)"
updates_aur="$(paru -Qua | wc -l)"
updates="$updates_regular&$updates_aur"

i3status | while :
do
	read line

	if [[ "$line" =~ ^'No battery | '.* ]]; then
		#line="$(echo $line | awk '{print substr($0, 15)}')"
		line="${line:13}"
	fi

	keyboard="$(xkblayout-state print \"%s\")"
	keyboard="${keyboard:1:-1}"

	netspeed="$($netspeed_file)"

	echo "$updates | ${netspeed}${line} | $keyboard"
done
