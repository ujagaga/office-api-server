#!/usr/bin/env bash

sudo apt install -y python3-pip ustreamer

python3 -m venv .venv
source .venv/bin/activate
pip3 install flask bcrypt opencv-python

chmod +x index.py

SERVICE_NAME=officeserver.service
SERVICE_FILE=/etc/systemd/system/$SERVICE_NAME

## Create new startup service 
{
echo "[Unit]"
echo Description=Office Server
echo After=network-online.target
echo Wants=network-online.target
echo StartLimitIntervalSec=0
echo
echo "[Service]"
echo Type=simple
echo User=$USER
echo ExecStart=$PWD/run_server.sh
echo WorkingDirectory=$PWD
echo
echo "[Install]"
echo WantedBy=multi-user.target
} > $PWD/$SERVICE_NAME
sudo mv $SERVICE_NAME $SERVICE_FILE

## Run the service 
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME
