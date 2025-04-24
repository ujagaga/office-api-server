#!/usr/bin/env bash

SERVICE_NAME=officeserver.service
SERVICE_FILE=/etc/systemd/system/$SERVICE_NAME

# --- Installation Section ---
echo "Installing dependencies..."
sudo apt update -y
sudo apt install -y python3-pip ustreamer

echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
pip3 install flask bcrypt opencv-python

echo "Making index.py executable..."
chmod +x index.py

# --- Service File Creation ---
echo "Creating systemd service file: $SERVICE_FILE"
cat <<EOF > "$PWD/$SERVICE_NAME"
[Unit]
Description=Office Server
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=$USER
ExecStart=$PWD/run_server.sh
WorkingDirectory=$PWD
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
sudo mv "$PWD/$SERVICE_NAME" "$SERVICE_FILE"

# --- Service Management ---
echo "Enabling and starting the service..."
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo "Office Server installation and service started successfully!"
