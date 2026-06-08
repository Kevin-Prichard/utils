#!/usr/bin/env bash

FIND_USER=`id|perl -ane '($n)=$_=~m|\(([^)]+)\)|; print "$n"'`
echo FIND_USER=$FIND_USER
if [ $FIND_USER != 'root' ]; then
    echo Must be run as root 1>&2
    exit 1
fi


find * \
    -regextype egrep \
    -not -iregex "/(callisto|cdrom|dev|mnt|proc|run|sys|tmp).*" \
    -not -iwholename "/swapfile.iso" \
    -type f
