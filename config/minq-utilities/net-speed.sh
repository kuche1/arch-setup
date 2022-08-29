#! /usr/bin/env bash

#
# Single interface:
# ifaces="eth0"
#
# Multiple interfaces:
# ifaces="eth0 wlan0"
#

# Auto detect interfaces
ifaces=$(ls /sys/class/net | grep -E '^(eno|enp|ens|enx|eth|wlan|wlp)')

readable() {
    local bytes=$1
    local kib=$(( bytes >> 10 ))
    if [ $kib -lt 0 ]; then
        echo "?K"
    elif [ $kib -gt 1024 ]; then
        local mib_int=$(( kib >> 10 ))
        local mib_dec=$(( kib % 1024 * 976 / 10000 ))
        if [ "$mib_dec" -lt 10 ]; then
          mib_dec="0${mib_dec}"
        fi
        echo "${mib_int}.${mib_dec}M"
    else
        echo "${kib}K"
    fi
}

for iface in $ifaces; do
    file_time="/tmp/net_usage_detector_${iface}_time"
    file_recv="/tmp/net_usage_detector_${iface}_recv"
    file_sent="/tmp/net_usage_detector_${iface}_sent"

    if [ -f "$file_time" ]; then
        read time_old < "$file_time"
    else
        time_=0
    fi

    if [ -f "$file_recv" ]; then
        read recv_old < "$file_recv"
    else
        recv_old=0
    fi

    if [ -f "$file_sent" ]; then
        read sent_old < "$file_sent"
    else
        sent_old=0
    fi

    time_="$(date +%s)"
    read recv < "/sys/class/net/${iface}/statistics/rx_bytes"
    read sent < "/sys/class/net/${iface}/statistics/tx_bytes"

    time_diff=$(( time_ - time_old ))
    recv_diff=$(( recv - recv_old ))
    sent_diff=$(( sent - sent_old ))

    echo "$time_" > "$file_time"
    echo "$recv" > "$file_recv"
    echo "$sent" > "$file_sent"

	if [ "$time_diff" = "0" ]; then
		recv="ERR"
		sent="ERR"
		time_=0
	else
		recv=$(( $recv_diff / $time_diff ))
		sent=$(( $sent_diff / $time_diff ))

		time_="$time_diff"
    	recv=$(readable $recv)
    	sent=$(readable $sent)
	fi

    printf "${iface} ${recv}↓ ${sent}↑ ${time_}s"
done

echo ""
