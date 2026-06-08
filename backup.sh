#!/usr/bin/env bash

RDIFF_USER=`id|perl -ane '($n)=$_=~m|\(([^)]+)\)|; print "$n"'`
echo RDIFF_USER=$RDIFF_USER
if [ $RDIFF_USER != 'root' ]; then
    echo Must be run as root 1>&2
    exit 1
fi

BACKUP_SOURCE=/
BACKUP_DEST=/callisto/scarps/ganymede
BACKUP_LOGS=$BACKUP_DEST-logs
BACKUP_LOG=${BACKUP_LOGS}/`date +%Y%m%d-%H%M%S`.log
RDIFF_PREFIX=/usr/local
RDIFF_HOME=$RDIFF_PREFIX/bin

if [ ! -d "$BACKUP_DEST" ]; then
    mkdir $BACKUP_DEST
fi
if [ ! -d "$BACKUP_LOGS" ]; then
    mkdir $BACKUP_LOGS
fi

$RDIFF_HOME/rdiff-backup --new -v5 $@ --api-version 201 $@ backup \
    --print-statistics \
    --exclude /callisto\*\* \
    --exclude /dev \
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
    --exclude /mnt \
    --exclude /proc \
    --exclude /run \
    --exclude /sys \
    --exclude /tmp \
    --exclude /var/tmp \
    --exclude /home/kev/snap/\*/\*\*/.cache \
    --exclude /home/kev/.cache \
    --exclude /home/kev/projs/\*/venv\*\* \
    --exclude /home/kev/snap/chromium/common/chromium/Default/Cache \
    --exclude /opt/tor-browser/Browser/Downloads \
    --exclude /home/kev/.config/Slack \
    --exclude home/kev/.local/share/Trash \
    $BACKUP_SOURCE $BACKUP_DEST >$BACKUP_LOG 2>&1 &

echo log: $BACKUP_LOG

RDIFF_PID=$!
echo Backup pid: $RDIFF_PID

tail -f $BACKUP_LOG

echo log: $BACKUP_LOG
