# office-api-server
My personal server with API for various automations. Based on FastAPI, it is intended to support embedded devices, 
so the authorization process is not very complex and not overly secure. To create a new user account or modify an xisting one:

    tools/edit_user.py -h


## Installing

    sudo apt install -y uvicorn python3-pip ustreamer
    pip3 install fastapi python-multipart requests sqlalchemy jinja2 paho-mqtt
    
To support translators for the weather page, install rust and python translators

    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    sudo apt install -y python3-dev ustreamer libxml2-dev libxslt-dev libffi-dev
    pip3 install translators


Run the server

    uvicorn sql_app.main:app --reload --host 0.0.0.0

## Authorization

To use this system an application must first login using username and password. The server will respond with a token. 
All further requests must provide this token as a http query parameter for API access or via browser cookie for the rest. 

## MQTT

An MQTT server is also available on the server, so we can add custom API endpoints to interact with it.
To install it:

    sudo apt install -y mosquitto

To configure:

    sudo nano /etc/mosquitto/conf.d/default.conf

Then paste:

    per_listener_settings false
    allow_anonymous false
    password_file /etc/mosquitto/passwd
    bind_address 0.0.0.0

Create password file:

    sudo mosquitto_passwd -c /etc/mosquitto/passwd <USER_NAME>

Restart Mosquitto:
    
    sudo systemctl restart mosquitto

## Streaming video from a webcam

    sudo apt install ustreamer
    ustreamer --host=0.0.0.0 --port=8013 --device=/dev/video1 --drop-same-frames=30 --slowdown --user <username> --passwd <password>
