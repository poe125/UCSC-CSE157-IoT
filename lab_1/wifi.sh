#!/bin/bash

echo
echo "Linux-based OS UCSC Eduroam connector by Frzvfdr"
echo
read -p "Enter your Cruz ID: " identity
read -s -p "Enter your Gold password: " password
echo  

wifi_config=$(cat <<EOF
network={
    ssid="eduroam"
    key_mgmt=WPA-EAP
    eap=PEAP
    identity="$identity"
    password="$password"
    phase1="peapver=0"
    phase2="MSCHAPV2"
}
EOF
)

sudo sed -i '/^network={/,/^}/d' /etc/wpa_supplicant/wpa_supplicant.conf
echo "$wifi_config" | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null


sudo systemctl restart dhcpcd

echo "Enjoy the UCSC's Eduroam!!"
