import hashlib
import string
import random
import subprocess
import os
import socket
import serial

current_dir = os.path.dirname(__file__)
ustreamer_script = os.path.join(current_dir, "..", "tools", "ustreamer.sh")
SERIAL_PORT = "/dev/ttyS3"


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


def start_webcam_stream():
    result = subprocess.run([ustreamer_script, "/tmp", "start"])
    return result.returncode


def stop_webcam_stream():
    result = subprocess.run([ustreamer_script, "/tmp", "stop"])
    return result.returncode


def printer_power(turn_on=False):
    if turn_on:
        cmd = bytearray([0xa5, 1])
    else:
        cmd = bytearray([0xa5, 0])

    ser = serial.Serial(SERIAL_PORT, 9600)
    ser.write(cmd)
    ser.close()
