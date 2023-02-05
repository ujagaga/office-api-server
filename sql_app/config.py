TOKEN_DURATION = 60 * 60 * 24   # 1 day
SQLALCHEMY_DATABASE_URL = 'sqlite:///./sql_app.db'
UNLOCK_OFFICE_URL = "http://192.168.0.151"
UNLOCK_OFFICE_PARAMS = {"key": "St1Nidz@13"}
MQTT_SERVER = "ujagaga.tplinkdns.com"
MQTT_INTERCOM_TOPIC = "intercom_door"
MQTT_OFFICE_LIGHT_TOPIC = "office_light"
MQTT_BAR_LIGHT_TOPIC = "bar_light"
MQTT_PORT = 1883
MQTT_USER = "ujagaga"
MQTT_PASS = "S1mpleTh1ngsM@tter"
USTREAMER_USER = "uStreamerUser"
TMP_DIR = "/tmp/officeserver"
USTREAMER_STATIC_DIR_SRC = "../tools/ustreamer_static"
USTREAMER_STATIC_DIR_DST = "ustreamer_static"
OFFICE_LIGHT_URL = "http://192.168.0.153"
LOCAL_USER_NAME = "local"

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
LOCATIONS = {
    "Novi Sad": {"latitude": "45.26", "longitude": "19.82"},
    "Velika Plana": {"latitude": "44.33", "longitude": "21.07"},
    "Kikinda": {"latitude": "45.83", "longitude": "20.48"},
    "Beograd": {"latitude": "44.78", "longitude": "20.47"},
}
DEFAULT_CITY = "Novi Sad"
WEATHER_NOT_READABLE_SECONDS = (60 * 30)
TODAY_MAX_HOURS = 25     # 24 hours max display plus current hour
DEFAULT_PARMS = {
    "latitude": "45.26",
    "longitude": "19.82",
    "hourly": "temperature_2m,weathercode,precipitation",
    "timezone": "auto",
    "daily": 'weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset'
}

LANGS = ["en", "sr"]
DEFAULT_LANG = "sr"

WEATHER_CODES = {
    0: {"en": "Clear sky", "sr": "Vedro", "icon": "c01"},
    1: {"en": "Mainly clear", "sr": "Uglavnom vedro", "icon": "c02"},
    2: {"en": "Partly cloudy", "sr": "Delimično oblačno", "icon": "c03"},
    3: {"en": "Overcast", "sr": "Oblačno", "icon": "c04"},
    45: {"en": "Fog", "sr": "Magla", "icon": "a01"},
    48: {"en": "Depositing rime fog", "sr": "Taloženje magle", "icon": "a01"},
    51: {"en": "Light drizzle", "sr": "Slaba kiša", "icon": "d01"},
    53: {"en": "Moderate drizzle", "sr": "Umerena kiša", "icon": "d01"},
    55: {"en": "Dense drizzle", "sr": "Gusta kiša", "icon": "d01"},
    56: {"en": "Light freezing drizzle", "sr": "Slaba ledena kiša", "icon": "d01"},
    57: {"en": "Dense feezing drizzle", "sr": "Gusta ledena kiša", "icon": "d01"},
    61: {"en": "Slight rain", "sr": "Slaba kiša", "icon": "r01"},
    63: {"en": "Moderate rain", "sr": "Umerena kiša", "icon": "r01"},
    65: {"en": "Heavy", "sr": "Jaka kiša", "icon": "r01"},
    66: {"en": "Light freezing rain", "sr": "Slaba ledena kiša", "icon": "f01"},
    67: {"en": "Heavy freezing rain", "sr": "Jaka ledena kiša", "icon": "f01"},
    71: {"en": "Slight snow", "sr": "Slab sneg", "icon": "s01"},
    73: {"en": "Moderate snow", "sr": "Umeren sneg", "icon": "s01"},
    75: {"en": "Heavy snow", "sr": "Gust sneg", "icon": "s01"},
    77: {"en": "Snow grains", "sr": "Ledeni sneg", "icon": "s01"},
    80: {"en": "Slight rain showers", "sr": "Laki pljuskovi", "icon": "r01"},
    81: {"en": "Moderate rain showers", "sr": "Umereni pljuskovi", "icon": "r01"},
    82: {"en": "Violent rain showers", "sr": "Jaki pljuskovi", "icon": "r02"},
    85: {"en": "Slight snow showers", "sr": "Slab sneg", "icon": "s01"},
    86: {"en": "Heavy snow showers", "sr": "Jak sneg", "icon": "s01"},
    95: {"en": "Thunderstorm", "sr": "Grmljavina", "icon": "t01"},
    96: {"en": "Thunderstorm with slight hail", "sr": "Grmljavina sa slabim gradom", "icon": "t02"},
    99: {"en": "Thunderstorm with heavy hail", "sr": "Grmljavina sa jakim gradom", "icon": "t02"},
}

WEEK_DAYS = {
    0: {"en": "Monday", "sr": "Ponedeljak"},
    1: {"en": "Tuesday", "sr": "Utorak"},
    2: {"en": "Wednesday", "sr": "Sreda"},
    3: {"en": "Thursday", "sr": "Četvrtak"},
    4: {"en": "Friday", "sr": "Petak"},
    5: {"en": "Saturday", "sr": "Subota"},
    6: {"en": "Sunday", "sr": "Nedelja"}
}
