#!/bin/sh
#
# wps-connect
#
# This script realized a WPS connection to a compatible WIFI router.
# The WIFI router must be in WPS mode before launching this script.
#
# This script must be started as sudo
#
# Returns :
readonly RET_OK=0
readonly RET_FAIL_NO_WPS_ROUTER_FOUND=1
readonly RET_FAIL_TO_CONNECT_TO_WPS_ROUTER=2
readonly RET_FAIL_NO_WIFI_INTERFACE=3
#

logFile="/tmp/wps-connect.log"

echo "Starting at $(date)...." >> $logFile 2>&1

echo 'WPS-CONNECT> Check wlan0 interface...' >> $logFile 2>&1
ifconfig wlan0 > /dev/null
if [ $? -ne 0 ] ; then
   echo 'WPS-CONNECT> ERROR : no WIFI interface found' >> $logFile 2>&1
   exit $RET_FAIL_NO_WIFI_INTERFACE
fi


echo 'WPS-CONNECT> Try to connect to a WIFI network...' >> $logFile 2>&1
wpa_cli scan > /dev/null
if [ $? -ne 0 ] ; then
   echo 'WPS-CONNECT> ERROR : fail to scan WIFI networks' >> $logFile 2>&1
   exit $RET_FAIL_NO_WIFI_INTERFACE
fi

# Seems that scan need a bit of time before scan results
sleep 2

echo 'WPS-CONNECT> Search for all networks WPS in WPS_PBC mode (WPS push button pressed), and select the closer (higher RSSI)...' >> $logFile 2>&1
routerMacAddress=$(wpa_cli scan_results | grep WPS-PBC | sort -r -k3 | awk 'END{print $1}')
if [ -z "$routerMacAddress" ] ; then
   echo 'WPS-CONNECT> ERROR : no WPS router in WPS_PBC mode found' >> $logFile 2>&1
   exit $RET_FAIL_NO_WPS_ROUTER_FOUND
fi

echo "WPS-CONNECT> Found a WPS router in WPS_PBC mode (WPS push button pressed) at '$routerMacAddress'. Try to connect..." >> $logFile 2>&1
wpa_cli wps_pbc $routerMacAddress
if [ $? -ne 0 ] ; then
   echo 'WPS-CONNECT> ERROR : fail to connect to WPS router' >> $logFile 2>&1
   exit $RET_FAIL_TO_CONNECT_TO_WPS_ROUTER
fi

ipAddress=$(ifconfig wlan0 | grep 'inet addr:' | cut -d: -f2 | awk '{print $1}')
echo "WPS-CONNECT> SUCCESS, connected as '$ipAddress'" >> $logFile 2>&1
exit $RET_OK
