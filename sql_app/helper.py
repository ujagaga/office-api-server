import hashlib
import string
import random
import requests
import paho.mqtt.client as paho
from . import config
import subprocess
import os
import shutil
import socket
import json
import translators as ts

current_dir = os.path.dirname(__file__)
ustreamer_script = os.path.join(current_dir, "..", "tools", "ustreamer.sh")
ustreamer_static_dir_src = os.path.join(current_dir, config.USTREAMER_STATIC_DIR_SRC)
ustreamer_static_dir_dst = os.path.join(config.TMP_DIR, config.USTREAMER_STATIC_DIR_DST)


city_ids = {
    "NOVI SAD": "3194360",
    "VELIKA PLANA": "784630",
    "KIKINDA": "789518"
}


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
    return server_subnet in ip_addr


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
    mqtt_client.username_pw_set(config.MQTT_USER, config.MQTT_PASS)
    mqtt_client.connect(config.MQTT_SERVER, config.MQTT_PORT)
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

        content = content.replace('{{stream_user}}', config.USTREAMER_USER)
        content = content.replace('{{stream_pwd}}', password)

        index_file = open(os.path.join(ustreamer_static_dir_dst, "index.html"), "w")
        index_file.write(content)
        index_file.close()

    except Exception as e:
        print("ERROR adjusting index file", e)

    result = subprocess.run([ustreamer_script, ustreamer_static_dir_dst, "start", config.USTREAMER_USER, password])
    return result.returncode


def stop_webcam_stream():
    result = subprocess.run([ustreamer_script, ustreamer_static_dir_dst, "stop"])
    return result.returncode


def translate_text(message, language='sr-Latn') -> str:
    return ts.translate_text(query_text=message, translator='bing', to_language=language)


def get_current_weather(city_name: str = config.DEFAULT_CITY) -> dict:

    city_id = city_ids.get(city_name.upper(), config.DEFAULT_CITY)

    url_params = {'key': config.WEATHER_API_KEY, 'city_id': city_id, 'lang': 'en'}
    r = requests.get(config.WEATHER_API_URL, params=url_params)
    status = "ERROR"
    try:
        if r.status_code == 200:
            json_ret_val = json.loads(r.text)
            data = json_ret_val['data'][0]
            temp = data['temp']
            weather = data['weather']
            description = translate_text(weather['description'])
            weather_code = weather['code']
            temp_str = f"{temp}".replace('.', ',')
            status = "OK"

            detail = {
                "city": data["city_name"],
                "weather": description,
                "temp": temp_str,
                "wind_spd": data["wind_spd"],
                "temp_feel": data["app_temp"],
                "cloud_coverage": data["clouds"],
                "part_of_day": data["pod"],
                "time": data["ob_time"],
                "weather_code": weather_code,
                "weather_icon": weather['icon']
            }

        else:
            status_code = r.status_code
            status_msg = r.text
            if status_code == 429:
                status_msg = "Dnevna granica dostignuta. Pokušajte sutra."
            detail = {"code": status_code, "message": status_msg}
    except Exception as e:
        detail = {"code": "", "message": f"{e}"}

    return {"status": status, "detail": detail}

