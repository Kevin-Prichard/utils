#!/usr/bin/env bash

while [ 1 ]; do
    RX=$(( 1 + $RANDOM % 100 - 50 ))
    RY=$(( 1 + $RANDOM % 100 - 50 ))
    echo $RX $RY
    # xdotool windowraise 29361931
    xdotool mousemove_relative -- $RX $RY
    sleep 5
done
