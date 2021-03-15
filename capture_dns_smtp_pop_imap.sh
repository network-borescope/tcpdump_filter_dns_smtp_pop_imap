#!/bin/sh
FILE=`date +udp_smtp_pop_imap_%Y%m%d_%H%M%S.txt`
INTERFACE="enp6s0f1"
N=200000
DNS="udp dst port 53"
SMTP="tcp dst port 25"
POP="tcp dst port 110"
POPC="tcp dst port 995"
IMAP="tcp dst port 143"
IMAPC="tcp dst port 993"
sudo tcpdump -i "$INTERFACE" -l -U -vvv -n -tttt -c "$N" "$DNS" or "$SMTP" or "$POP" or "$POPC" or "$IMAP" or "$IMAPC" > "/home/borescope/tools/udp_smtp_pop_imap/data/$FILE"
