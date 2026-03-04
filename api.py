# api.py

import requests


# =============================
# API KEYS
# =============================

WEATHERAPI_KEY = "8c7a24be876f4df99f0153444260403"
VISUAL_KEY = "MYHCGC7NJHBR8VLRFXJF8YFHF"


# =============================
# HELPERS
# =============================

def _safe(d, key):

    if d and key in d:
        return d[key]

    return None


# =============================
# GEO
# =============================

def get_coords(city):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    r = requests.get(url, params={
        "name": city,
        "count": 1
    }).json()

    if "results" not in r:
        return None, None

    p = r["results"][0]

    return p["latitude"], p["longitude"]


# =============================
# OPEN METEO
# =============================

def openmeteo_current(city):

    lat, lon = get_coords(city)

    if not lat:
        return None


    url = "https://api.open-meteo.com/v1/forecast"

    r = requests.get(url, params={
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "relativehumidity_2m,precipitation,uv_index",
        "timezone": "auto"
    }).json()


    cur = r["current_weather"]
    hour = r["hourly"]


    return {
        "temp": cur["temperature"],
        "wind": cur["windspeed"],
        "code": cur["weathercode"],

        "humidity": hour["relativehumidity_2m"][0],
        "precip": hour["precipitation"][0],
        "uv": hour["uv_index"][0]
    }


def openmeteo_hourly(city):

    lat, lon = get_coords(city)

    if not lat:
        return None


    r = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat,
        "longitude": lon,

        "hourly": [
            "temperature_2m",
            "weathercode",
            "relativehumidity_2m",
            "precipitation"
        ],

        "timezone": "auto"
    }).json()


    data = []

    for i in range(24):

        data.append({
            "time": r["hourly"]["time"][i],
            "temp": r["hourly"]["temperature_2m"][i],
            "humidity": r["hourly"]["relativehumidity_2m"][i],
            "precip": r["hourly"]["precipitation"][i],
            "code": r["hourly"]["weathercode"][i]
        })


    return data


def openmeteo_tomorrow(city):

    lat, lon = get_coords(city)

    if not lat:
        return None


    r = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat,
        "longitude": lon,

        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "weathercode",
            "uv_index_max",
            "precipitation_sum"
        ],

        "timezone": "auto"
    }).json()


    return {
        "date": r["daily"]["time"][1],

        "max": r["daily"]["temperature_2m_max"][1],
        "min": r["daily"]["temperature_2m_min"][1],

        "uv": r["daily"]["uv_index_max"][1],
        "precip": r["daily"]["precipitation_sum"][1],

        "code": r["daily"]["weathercode"][1]
    }


def openmeteo_week(city):

    lat, lon = get_coords(city)

    if not lat:
        return None


    r = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat,
        "longitude": lon,

        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "weathercode",
            "uv_index_max",
            "precipitation_sum"
        ],

        "timezone": "auto"
    }).json()


    out = []


    for i in range(len(r["daily"]["time"])):

        out.append({
            "date": r["daily"]["time"][i],

            "max": r["daily"]["temperature_2m_max"][i],
            "min": r["daily"]["temperature_2m_min"][i],

            "uv": r["daily"]["uv_index_max"][i],
            "precip": r["daily"]["precipitation_sum"][i],

            "code": r["daily"]["weathercode"][i]
        })


    return out


# =============================
# WEATHERAPI.COM
# =============================

def weatherapi_current(city):

    r = requests.get("https://api.weatherapi.com/v1/current.json", params={
        "key": WEATHERAPI_KEY,
        "q": city
    }).json()


    c = r["current"]


    return {
        "temp": c["temp_c"],
        "wind": c["wind_kph"],
        "humidity": c["humidity"],
        "uv": c["uv"],
        "precip": c["precip_mm"],
        "code": c["condition"]["code"]
    }


def weatherapi_hourly(city):

    r = requests.get("https://api.weatherapi.com/v1/forecast.json", params={
        "key": WEATHERAPI_KEY,
        "q": city,
        "days": 1
    }).json()


    hours = r["forecast"]["forecastday"][0]["hour"]


    out = []


    for h in hours[:24]:

        out.append({
            "time": h["time"],

            "temp": h["temp_c"],
            "humidity": h["humidity"],
            "precip": h["precip_mm"],
            "code": h["condition"]["code"]
        })


    return out


def weatherapi_tomorrow(city):

    r = requests.get("https://api.weatherapi.com/v1/forecast.json", params={
        "key": WEATHERAPI_KEY,
        "q": city,
        "days": 2
    }).json()


    d = r["forecast"]["forecastday"][1]["day"]


    return {
        "date": r["forecast"]["forecastday"][1]["date"],

        "max": d["maxtemp_c"],
        "min": d["mintemp_c"],

        "uv": d["uv"],
        "precip": d["totalprecip_mm"],

        "code": d["condition"]["code"]
    }


def weatherapi_week(city):

    r = requests.get("https://api.weatherapi.com/v1/forecast.json", params={
        "key": WEATHERAPI_KEY,
        "q": city,
        "days": 7
    }).json()


    out = []


    for d in r["forecast"]["forecastday"]:

        out.append({
            "date": d["date"],

            "max": d["day"]["maxtemp_c"],
            "min": d["day"]["mintemp_c"],

            "uv": d["day"]["uv"],
            "precip": d["day"]["totalprecip_mm"],

            "code": d["day"]["condition"]["code"]
        })


    return out


# =============================
# VISUAL CROSSING
# =============================

def visual_current(city):

    r = requests.get(
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/today",
        params={
            "key": VISUAL_KEY,
            "unitGroup": "metric"
        }
    ).json()


    d = r["currentConditions"]


    return {
        "temp": d["temp"],
        "wind": d["windspeed"],
        "humidity": d["humidity"],
        "uv": d["uvindex"],
        "precip": d["precip"],
        "code": d["icon"]
    }


def visual_hourly(city):

    r = requests.get(
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}",
        params={
            "key": VISUAL_KEY,
            "unitGroup": "metric"
        }
    ).json()


    out = []


    for h in r["days"][0]["hours"][:24]:

        out.append({
            "time": h["datetime"],

            "temp": h["temp"],
            "humidity": h["humidity"],
            "precip": h["precip"],
            "code": h["icon"]
        })


    return out


def visual_tomorrow(city):

    r = requests.get(
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}",
        params={
            "key": VISUAL_KEY,
            "unitGroup": "metric"
        }
    ).json()


    d = r["days"][1]


    return {
        "date": d["datetime"],

        "max": d["tempmax"],
        "min": d["tempmin"],

        "uv": d["uvindex"],
        "precip": d["precip"],

        "code": d["icon"]
    }


def visual_week(city):

    r = requests.get(
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}",
        params={
            "key": VISUAL_KEY,
            "unitGroup": "metric"
        }
    ).json()


    out = []


    for d in r["days"][:7]:

        out.append({
            "date": d["datetime"],

            "max": d["tempmax"],
            "min": d["tempmin"],

            "uv": d["uvindex"],
            "precip": d["precip"],

            "code": d["icon"]
        })


    return out


# =============================
# AGGREGATORS (FOR AI)
# =============================

def get_all_current(city):

    return {
        "openmeteo": openmeteo_current(city),
        "weatherapi": weatherapi_current(city),
        "visual": visual_current(city)
    }


def get_all_hourly(city):

    return {
        "openmeteo": openmeteo_hourly(city),
        "weatherapi": weatherapi_hourly(city),
        "visual": visual_hourly(city)
    }


def get_all_tomorrow(city):

    return {
        "openmeteo": openmeteo_tomorrow(city),
        "weatherapi": weatherapi_tomorrow(city),
        "visual": visual_tomorrow(city)
    }


def get_all_week(city):

    return {
        "openmeteo": openmeteo_week(city),
        "weatherapi": weatherapi_week(city),
        "visual": visual_week(city)
    }