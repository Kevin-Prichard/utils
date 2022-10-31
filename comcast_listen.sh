#!/usr/bin/env bash

# Occasionally, packets appear on the Comcast router's interface
# which have no simple explanation. Once, I spotted a port scan
# os IPs under 73.0.0.1/8, with a source address linked to a
# known security researcher. At other times, packets originating
# from within Comcast's assigned IPs appear, usually on well-known
# ports like 21, 23, 23, 80, 443, 137, 138, 139, 445.

SELF_IP=$1
SELF_DEV=$2 || "enx8cae4cfee880"
if [[ "${SELF_IP}" = "" || "${SELF_DEV}" = "" ]]; then
    echo "Usage: comcast_listen.sh <self_ip_addr> <optional_ip_iface>"
    exit 99
fi

timestamp () {
    echo `date +%Y%m%d_%H%M%S`
}


start_dump () {
    IFACE=$1; CIDR=$2; SELF_IP=$3; FN_PREFIX=$4; PCAP_BASEPATH=$5; LOG_BASPATH=$6;
    FN="${FN_PREFIX}_`timestamp`";
    DUMP_CMD="tcpdump -v -s 99999 -w $PCAP_BASEPATH/$FN.pcap \\
             -i $IFACE network $CIDR not $SELF_IP 2>&1 > $LOG_BASPATH/$FN.log"
    echo $DUMP_CMD
    `${DUMP_CMD}` &
    PID=$?
    echo "${PID}"
}


main() {
    start_dump "${SELF_DEV}" "73.0.0.0/8" "${SELF_IP}/32" "ccpsv" "./captures" "./logs"
}

main $SELF_IP
