#!/usr/bin/env bash

SIZES_USER=`id|perl -ane '($n)=$_=~m|\(([^)]+)\)|; print "$n"'`
echo USER=$SIZES_USER
if [ $SIZES_USER != 'root' ]; then
    echo Must be run as root 1>&2
    exit 1
fi

du \
    --exclude /callisto\*\* \
    --exclude /swapfile.iso \
    --exclude /cdrom \
    --exclude /mnt/appimage \
    --exclude /mnt/D64 \
    --exclude /mnt/handbrake \
    --exclude /mnt/investi \
    --exclude /mnt/mancer \
    --exclude /mnt/media \
    --exclude /mnt/media-fat \
    --exclude /mnt/nestcam \
    --exclude /mnt/notion \
    --exclude /proc \
    --exclude /sys \
    --exclude /tmp \
    -hd 0 /
