import hashlib
import string
import random
import requests
import paho.mqtt.client as paho
from .config import MQTT_PORT, MQTT_PASS, MQTT_USER, MQTT_SERVER, USTREAMER_USER, TMP_DIR, USTREAMER_STATIC_DIR_SRC, \
    USTREAMER_STATIC_DIR_DST
import subprocess
import os
import shutil
import socket

current_dir = os.path.dirname(__file__)
ustreamer_script = os.path.join(current_dir, "..", "tools", "ustreamer.sh")
ustreamer_static_dir_src = os.path.join(current_dir, USTREAMER_STATIC_DIR_SRC)
ustreamer_static_dir_dst = os.path.join(TMP_DIR, USTREAMER_STATIC_DIR_DST)


def get_server_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def is_ip_local(ip_addr):
    server_ip = get_server_ip()
    ip_designator = server_ip.split(".")[-1]
    server_subnet = server_ip[:len(server_ip)-len(ip_designator)]
    print("***** SERVER SUBNET:", server_subnet)
    return False


def get_hashed_password(plain_text_password):
    return hashlib.sha256(plain_text_password.encode()).hexdigest()


def verify_password(plain_text_password, hashed_password):
    return get_hashed_password(plain_text_password) == hashed_password


def generate_token(token_len=32):
    return ''.join(random.choices(string.ascii_letters, k=token_len))


def http_get_query(url: str, params: dict = {}):
    response = requests.get(url=url, params=params)
    return response.text


def mqtt_publish(topic: str, message: str):
    print(f'Publishing "{message}" to topic "{topic}"')
    mqtt_client = paho.Client("OfficeServer")
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
    mqtt_client.connect(MQTT_SERVER, MQTT_PORT)
    status, code = mqtt_client.publish(topic, message)

    if status == 0:
        return "MQTT message sent"
    else:
        return f"ERROR sending MQTT message. status: {status}, code: {code}"


def start_webcam_stream(password):
    # Copy static folder to tmp
    os.makedirs(ustreamer_static_dir_dst, exist_ok=True)
    shutil.copytree(ustreamer_static_dir_src, ustreamer_static_dir_dst, dirs_exist_ok=True)

    lines = []
    try:
        index_file = open(os.path.join(ustreamer_static_dir_dst, "index.html"), "r")
        content = index_file.read()
        index_file.close()

        content = content.replace('{{stream_user}}', USTREAMER_USER)
        content = content.replace('{{stream_pwd}}', password)

        index_file = open(os.path.join(ustreamer_static_dir_dst, "index.html"), "w")
        index_file.write(content)
        index_file.close()

    except Exception as e:
        print("ERROR adjusting index file", e)

    result = subprocess.run([ustreamer_script, ustreamer_static_dir_dst, "start", USTREAMER_USER, password])
    return result.returncode


def stop_webcam_stream():
    result = subprocess.run([ustreamer_script, ustreamer_static_dir_dst, "stop"])
    return result.returncode
