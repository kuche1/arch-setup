#! /usr/bin/env bash

# create sinks and virtual mic
pactl load-module module-null-sink media.class=Audio/Sink sink_name=audio-sharing-sink channel_map=stereo
pactl load-module module-null-sink media.class=Audio/Sink sink_name=CONFIG-ONLY-audio-sharing-sync-volume channel_map=stereo
pactl load-module module-null-sink media.class=Audio/Source/Virtual sink_name=minq-virtualmic channel_map=front-left,front-right
# redirect real mic to virtual mic
pw-link alsa_input.usb-C-Media_Electronics_Inc._Redragon_Gaming_Headset-00.mono-fallback:capture_MONO minq-virtualmic:input_FL
	# find this by running `pw-link -o`
# redirect regular sink to lower volume sink
pw-link audio-sharing-sink:monitor_FL CONFIG-ONLY-audio-sharing-sync-volume:playback_FL
pw-link audio-sharing-sink:monitor_FR CONFIG-ONLY-audio-sharing-sync-volume:playback_FR
# redirect lower volume sink to virtual mic
pw-link CONFIG-ONLY-audio-sharing-sync-volume:monitor_FL minq-virtualmic:input_FL
pw-link CONFIG-ONLY-audio-sharing-sync-volume:monitor_FR minq-virtualmic:input_FR
# set volume on lower volume sink
pactl set-sink-volume CONFIG-ONLY-audio-sharing-sync-volume 50%
# connect regular sink to headphones
pw-link audio-sharing-sink:monitor_FL alsa_output.usb-C-Media_Electronics_Inc._Redragon_Gaming_Headset-00.analog-stereo:playback_FL
pw-link audio-sharing-sink:monitor_FR alsa_output.usb-C-Media_Electronics_Inc._Redragon_Gaming_Headset-00.analog-stereo:playback_FR
