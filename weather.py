from smart_weather import smart_weather


# =============================
# Format Current (AI)
# =============================

def format_current(city):

    data = smart_weather(city)

    if not data:
        return None


    lines = [
        f"City: {data['city']}",
        f"🌡️ Temperature: {data['temperature']} °C",
        f"💨 Wind: {data['wind']} km/h",
        f"💧 Humidity: {data['humidity']} %",
        f"☀️ UV Index: {data['uv']}",
        f"🌧️ Precipitation: {data['precip']} mm",
        f"🤖 Confidence: {data['confidence']}",
        f"📡 Sources: {', '.join(data['sources'])}"
    ]

    return lines


# =============================
# Hourly (Open-Meteo)
# =============================

import requests


def get_coordinates(city):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 1
    }

    r = requests.get(url, params=params).json()

    if "results" not in r:
        return None, None

    res = r["results"][0]

    return res["latitude"], res["longitude"]


def get_hourly(city):

    lat, lon = get_coordinates(city)

    if not lat:
        return None


    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,

        "hourly": [
            "temperature_2m",
            "relativehumidity_2m",
            "precipitation"
        ],

        "timezone": "auto"
    }

    return requests.get(url, params=params).json()["hourly"]


def format_hourly(city):

    data = get_hourly(city)

    if not data:
        return None


    lines = [f"Hourly forecast for {city}:"]


    for i in range(24):

        time = data["time"][i].split("T")[1]

        temp = data["temperature_2m"][i]
        hum = data["relativehumidity_2m"][i]
        rain = data["precipitation"][i]

        line = (
            f"{time} | "
            f"{temp}°C | "
            f"💧{hum}% | "
            f"🌧️{rain}mm"
        )

        lines.append(line)


    return lines


# =============================
# Daily / Week (Open-Meteo)
# =============================

def get_daily(city):

    lat, lon = get_coordinates(city)

    if not lat:
        return None


    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,

        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "uv_index_max"
        ],

        "timezone": "auto"
    }

    return requests.get(url, params=params).json()["daily"]


def format_tomorrow(city):

    d = get_daily(city)

    if not d:
        return None


    i = 1


    lines = [
        f"Tomorrow in {city} ({d['time'][i]})",

        f"🌡️ {d['temperature_2m_max'][i]} / {d['temperature_2m_min'][i]} °C",

        f"☀️ UV: {d['uv_index_max'][i]}",

        f"🌧️ Rain: {d['precipitation_sum'][i]} mm"
    ]


    return lines


def format_week(city):

    d = get_daily(city)

    if not d:
        return None


    lines = [f"7-Day forecast for {city}:"]


    for i in range(len(d["time"])):

        line = (
            f"{d['time'][i]} | "
            f"{d['temperature_2m_max'][i]}/"
            f"{d['temperature_2m_min'][i]}°C | "
            f"☀️UV {d['uv_index_max'][i]} | "
            f"🌧️{d['precipitation_sum'][i]}mm"
        )

        lines.append(line)


    return lines


# =============================
# Universal Getter
# =============================

def get_weather_lines(city, mode, by_hours=False):

    if mode == "day":

        if by_hours:
            return format_hourly(city)
        else:
            return format_current(city)

    elif mode == "week":
        return format_week(city)

    elif mode == "tomorrow":
        return format_tomorrow(city)

    elif mode == "now":
        return format_current(city)

    return None