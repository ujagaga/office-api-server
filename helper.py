import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config
import random
import string
import re
import time
import datetime
import bcrypt
import locale
import json
import database
import os
import subprocess
import cv2



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


def datetime_from_epoch(epoch_timestamp):
    """Converts an epoch timestamp (seconds since the Unix epoch) to a datetime object.
    Args:
        epoch_timestamp: The epoch timestamp (integer or float).
    Returns:
        A datetime object representing the time corresponding to the timestamp.
        Returns None if the input is invalid (e.g., non-numeric or negative).
    """
    try:
        return datetime.datetime.fromtimestamp(epoch_timestamp)
    except (TypeError, ValueError) as e:
        print(f"Invalid epoch timestamp: {e}")  # Handle the error appropriately
        return None


def timestamp_daily_range_from_epoch(epoch_timestamp, min_h=0, max_h=23):
    """Converts an epoch timestamp to the start and end of the day in UTC.

    Args:
        epoch_timestamp: The epoch timestamp (integer or float).
        min_h: Minimum day start hour (sometimes office worktime start time)
        max_h: maximum day end hour (sometimes office work end time)
    Returns:
        A tuple of epoch timestamps representing the start and end of the day in UTC.
        Returns None if the input is invalid.
    """
    try:
        utc_dt = datetime.datetime.fromtimestamp(epoch_timestamp, tz=datetime.timezone.utc)  # Correct way for UTC
        start_dt = utc_dt.replace(hour=min_h, minute=0, second=1)
        end_dt = utc_dt.replace(hour=max_h, minute=59, second=59)
        return int(time.mktime(start_dt.timetuple())), int(time.mktime(end_dt.timetuple()))
    except (TypeError, ValueError, OSError) as e: #Add OSError for invalid timestamps
        print(f"Invalid epoch timestamp: {e}")
        return None


def check_token_expired(user):
    try:
        if user.get("token") and (time.time() - int(user.get("timestamp"))) < config.TOKEN_DURATION:
           return False
    except ValueError:
        pass

    return True



def timestamp_past(epoch_timestamp):
    try:
        request_timestamp = int(epoch_timestamp)
        today_timestamp = int(time.time())
        utc_dt = datetime.datetime.fromtimestamp(today_timestamp, tz=datetime.timezone.utc)  # Correct way for UTC
        start_dt = utc_dt.replace(hour=0, minute=0, second=1)
        today_start_timestamp = int(time.mktime(start_dt.timetuple()))

        return request_timestamp < today_start_timestamp
    except (TypeError, ValueError, OSError) as e: #Add OSError for invalid timestamps
        print(f"Invalid epoch timestamp: {e}")
        return True


def try_to_int(number, default=None):
    try:
        ret_val = int(number)
    except:
        ret_val = default

    return ret_val


def timestamp_from_date_str(date_str, hour_str):
    try:
        datetime_str = f"{date_str} {hour_str}:00:00"
        dt = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        epoch_timestamp = int(dt.timestamp())

        return epoch_timestamp
    except:
        return None


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


def date_time_string_from_epoch(timestamp, user_locale):
    time_locale = f"{user_locale[0]}.{user_locale[1]}"
    locale.setlocale(locale.LC_TIME, time_locale)
    date_and_time = datetime.datetime.fromtimestamp(timestamp)
    retVal = date_and_time.strftime('%Y-%m-%d %A')
    time_locale = f"{config.APPLICATION_LOCALE[0]}.{config.APPLICATION_LOCALE[1]}"
    locale.setlocale(locale.LC_TIME, time_locale)
    return retVal


def run_ustreamer(start=True, resolution=config.VIDEO_RESOLUTION):

    if start:
        cmd = "start"
    else:
        cmd = "stop"

    script_path = os.path.join(current_path, config.USTREAMER_SCRIPT)
    subprocess.call([script_path, cmd, "0", resolution, f"{config.STREAM_TIMEOUT}"])


def check_supported_resolutions(camera_index=config.CAMERA_INDEX):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {camera_index}")
        return

    supported_resolutions = []

    # Try some common resolutions (you might need to experiment)
    test_resolutions = [(640, 480), (1280, 720), (1280, 960), (1280, 1024), (1920, 1080), (3840, 2160)]  # Example resolutions

    for width, height in test_resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        current_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        current_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if (current_width, current_height) == (width, height) and current_width != 0 and current_height != 0:
            supported_resolutions.append(f"{current_width}x{current_height}")

    cap.release()
    cv2.destroyAllWindows()

    return supported_resolutions
