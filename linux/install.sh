#!/bin/bash
if [ $(id -u) -ne 0 ]; then
	echo "Error: you must run this script as root."
	exit 1
fi
mkdir -p /opt/cloudown
cp -rdf * /opt/cloudown
rm /opt/cloudown/install.sh
chmod a+x /opt/cloudown/Cloudown
chmod 777 -R /opt/cloudown/logs
chmod 777 -R /opt/cloudown/aria2
chmod a+x /opt/cloudown/Cloudown.sh
chmod a+x /opt/cloudown/uninstall.sh
cp /opt/cloudown/Cloudown.desktop /usr/share/applications
echo "Install successed!"
exit 0
