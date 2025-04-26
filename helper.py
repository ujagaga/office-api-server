import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config
import random
import string
import re
import time
import bcrypt
import json
import database
import os
import subprocess

current_path = os.path.dirname(os.path.realpath(__file__))
lang_dir = os.path.join(current_path, 'lang')
DEFAULT_LANG_ID = "eng"
default_colors = config.COLOR_PROFILES[0]


def send_email(recipient, subject, body):
    """
    Sends an email using configured credentials.
    """
    # Create message
    msg = MIMEMultipart()
    msg["From"] = config.SMTP_USER
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to SMTP server without SSL
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.ehlo()

        # Login to the SMTP server
        server.login(config.SMTP_USER, config.SMTP_PASS)

        # Send email
        server.sendmail(config.SMTP_USER, recipient, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Error: {e}")


def hash_string(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def check_hashed_string(plan_string: str, hashed_string: str) -> bool:
    return bcrypt.checkpw(plan_string.encode(), hashed_string.encode())


def generate_token():
    random_str = random.choices(string.ascii_letters, k=16)
    unique_str = f"{random_str}{time.time()}"

    return hash_string(unique_str)


def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))


def check_token_expired(user):
    try:
        if user.get("token") and (time.time() - int(user.get("timestamp"))) < config.TOKEN_DURATION:
           return False
    except ValueError:
        pass

    return True


def try_to_int(number, default=None):
    try:
        ret_val = int(number)
    except:
        ret_val = default

    return ret_val


def load_language():
    for filename in os.listdir(lang_dir):
        file_path = os.path.join(lang_dir, filename)

        if not os.path.isfile(file_path):
            continue
        if not file_path.endswith(".lang"):
            continue

        try:
            f = open(file_path, 'r')
            lines = f.readlines()
            f.close()

            language = {}

            for line in lines:
                if line.startswith('#'):
                    continue
                if '=' not in line:
                    continue

                data = line.strip('\n').split('=')

                if len(data) == 2:
                    key = data[0].strip()
                    val = data[1].strip()
                    language[key] = val

            lang_id = filename.split(".")[0]
            words = json.dumps(language)

            database.update_language(language_id=lang_id, words=words)
        except:
            pass


def run_ustreamer(start=True, resolution=config.VIDEO_RESOLUTION, camera_index=config.CAMERA_INDEX):

    if start:
        cmd = "start"
    else:
        cmd = "stop"

    script_path = os.path.join(current_path, config.USTREAMER_SCRIPT)
    subprocess.call([script_path, cmd, f"{camera_index}", resolution, f"{config.STREAM_TIMEOUT}"])


def check_supported_resolutions(camera_index=config.CAMERA_INDEX):
    try:
        output = subprocess.check_output(
            ["v4l2-ctl", f"--device=/dev/video{camera_index}", "--list-formats-ext"],
            stderr=subprocess.STDOUT
        ).decode()
    except subprocess.CalledProcessError as e:
        print(f"Error calling v4l2-ctl: {e.output.decode()}")
        return []

    resolutions = {}
    for line in output.splitlines():
        match = re.search(r'\s+Size:\s+Discrete\s+(\d+)x(\d+)', line)
        if match:
            width, height = match.groups()
            width_int = width
            try:
                width_int = int(width)
            except ValueError:
                pass

            resolutions[width_int] = height

    sorted_list = []

    for key in sorted(resolutions.keys()):
        resolution = f"{key}x{resolutions[key]}"
        sorted_list.append(resolution)

    print("Sorted Resolutions: ", sorted_list)

    return sorted_list
