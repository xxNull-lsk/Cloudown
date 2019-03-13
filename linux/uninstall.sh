#!/bin/bash
if [ $(id -u) -ne 0 ]; then
	echo "Error: you must run this script as root."
	exit 1
fi
rm /usr/share/applications/Cloudown.desktop
rm -rf /opt/cloudown
echo "Install successed!"
exit 0
