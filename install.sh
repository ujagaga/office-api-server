#!/bin/bash

sudo apt install uvicorn python3-pip
pip install fastapi python-multipart requests sqlalchemy jinja2 paho-mqtt

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
echo ExecStart=uvicorn sql_app.main:app --reload --host 0.0.0.0 --port 8000
echo WorkingDirectory=$PWD
echo
echo "[Install]"
echo WantedBy=multi-user.target
} > $PWD/$SERVICE_NAME
sudo mv $SERVICE_NAME $SERVICE_FILE

## Run the service 
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

#uvicorn sql_app.main:app --reload --host 0.0.0.0 --port 443 --ssl-certfile /home/rada/certs/ujagaga.tplinkdns.com.pem --ssl-keyfile /home/rada/certs/ujagaga.tplinkdns.com-key.pem

