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
from datetime import datetime, timedelta
import urllib.parse

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


def get_weather_forcast(city_name: str = config.DEFAULT_CITY) -> dict:
    if city_name not in config.LOCATIONS.keys():
        city_name = config.DEFAULT_CITY
    city = config.LOCATIONS.get(city_name)
    if city is None:
        return {"status": "ERROR", "detail": "No valid city specified"}

    url_params = config.DEFAULT_PARMS
    url_params["latitude"] = city["latitude"]
    url_params["longitude"] = city["longitude"]

    payload_str = urllib.parse.urlencode(url_params, safe=',')
    r = requests.get(config.WEATHER_API_URL, params=payload_str)
    status = "ERROR"

    try:
        if r.status_code == 200:
            json_ret_val = json.loads(r.text)

            hourly_data = json_ret_val["hourly"]
            daily_data = json_ret_val["daily"]

            now = datetime.now()
            today_info = {}

            forcast_data = []

            for i in range(0, len(daily_data["time"])):
                item_date = datetime.strptime(daily_data["time"][i], '%Y-%m-%d')
                weather_code = daily_data["weathercode"][i]
                temp_min = daily_data["temperature_2m_min"][i]
                temp_max = daily_data["temperature_2m_max"][i]

                icon_name = None
                description = config.WEATHER_CODES.get(weather_code, None)

                day_name = config.WEEK_DAYS[item_date.weekday()][config.DEFAULT_LANG]
                if item_date.date() == datetime.now().date():

                    today_info = {
                        "day": day_name,
                        "temp_min": temp_min,
                        "temp_max": temp_max,
                        "sunrise": daily_data["sunrise"][i],
                        "sunset": daily_data["sunset"][i],
                    }
                else:
                    if description is not None:
                        icon_name = f"{description['icon']}d"

                    forcast_data.append({
                        "day": day_name,
                        "date": f"{ item_date.day }.{ item_date.month }",
                        "temp_min": int(temp_min + 0.5),
                        "temp_max": int(temp_max + 0.5),
                        "icon": icon_name
                    })

            today_data = []

            start_time = now - timedelta(hours=1)
            end_time = start_time + timedelta(hours=config.TODAY_MAX_HOURS)

            for i in range(0, len(hourly_data["time"])):
                item_time = datetime.strptime(hourly_data["time"][i], '%Y-%m-%dT%H:%M')
                if start_time <= item_time <= end_time:

                    temperature = hourly_data["temperature_2m"][i]
                    weather_code = hourly_data["weathercode"][i]
                    description = config.WEATHER_CODES.get(weather_code, None)
                    precipitation = hourly_data["precipitation"][i]

                    if description is not None and today_info is not None:
                        sunrise = datetime.strptime(today_info["sunrise"], '%Y-%m-%dT%H:%M')
                        sunset = datetime.strptime(today_info["sunset"], '%Y-%m-%dT%H:%M')

                        if sunrise.time() < item_time.time() < sunset.time():
                            icon_name = f"{description['icon']}d"
                        else:
                            icon_name = f"{description['icon']}n"

                        if item_time.replace(minute=0) <= now < (item_time.replace(minute=0) + timedelta(hours=1)):
                            today_info["weather_code"] = weather_code
                            today_info["description"] = description.get(config.DEFAULT_LANG, "No translation available")
                            today_info["icon_name"] = icon_name
                            today_info["temp"] = int(temperature + 0.5)
                        else:
                            interval_data = {
                                "hour": item_time.hour,
                                "temp": temperature,
                                "icon_name": icon_name,
                                "prec": precipitation,
                                "wc": weather_code
                            }
                            today_data.append(interval_data)

            detail = {"city_name": city_name, "today_info": today_info, "hourly": today_data, "daily": forcast_data}

            status = "OK"

        else:
            json_ret_val = json.loads(r.text)
            detail = {"code": r.status_code, "message": json_ret_val["reason"]}
    except Exception as e:
        detail = {"code": "", "message": f"ERROR: {e}"}

    return {"status": status, "detail": detail}
