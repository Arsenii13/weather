import requests
import statistics
import os
import json
import time


# ===============================
# CONFIG
# ===============================

WEATHERAPI_KEY = "8c7a24be876f4df99f0153444260403"
VISUAL_KEY = "MYHCGC7NJHBR8VLRFXJF8YFHF"

HISTORY_FILE = "weather_history.json"
WEIGHTS_FILE = "api_weights.json"


# ===============================
# INIT STORAGE
# ===============================

def init_files():

    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)

    if not os.path.exists(WEIGHTS_FILE):

        weights = {
            "open-meteo": 1.0,
            "weatherapi": 1.0,
            "visualcrossing": 1.0
        }

        with open(WEIGHTS_FILE, "w") as f:
            json.dump(weights, f, indent=2)


init_files()


# ===============================
# FILE HELPERS
# ===============================

def load_weights():
    with open(WEIGHTS_FILE) as f:
        return json.load(f)


def save_weights(w):
    with open(WEIGHTS_FILE, "w") as f:
        json.dump(w, f, indent=2)


def save_history(data):

    with open(HISTORY_FILE) as f:
        hist = json.load(f)

    hist.append(data)

    with open(HISTORY_FILE, "w") as f:
        json.dump(hist, f, indent=2)


# ===============================
# API: OPEN METEO
# ===============================

def open_meteo(city):

    try:
        # Geocoding
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=10
        ).json()

        if "results" not in geo:
            return None

        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]


        # Weather
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,

                "current_weather": True,

                "hourly": [
                    "relativehumidity_2m",
                    "precipitation"
                ],

                "daily": [
                    "uv_index_max"
                ],

                "timezone": "auto"
            },
            timeout=10
        ).json()


        w = r["current_weather"]


        return {
            "temp": w["temperature"],
            "wind": w["windspeed"],

            "humidity": r["hourly"]["relativehumidity_2m"][0],
            "precip": r["hourly"]["precipitation"][0],
            "uv": r["daily"]["uv_index_max"][0],

            "source": "open-meteo"
        }

    except:
        return None


# ===============================
# API: WEATHERAPI
# ===============================

def weatherapi(city):

    if not WEATHERAPI_KEY:
        return None

    try:
        r = requests.get(
            "https://api.weatherapi.com/v1/current.json",
            params={
                "key": WEATHERAPI_KEY,
                "q": city
            },
            timeout=10
        ).json()


        c = r["current"]


        return {
            "temp": c["temp_c"],
            "wind": c["wind_kph"],

            "humidity": c["humidity"],
            "uv": c["uv"],
            "precip": c["precip_mm"],

            "source": "weatherapi"
        }

    except:
        return None


# ===============================
# API: VISUAL CROSSING
# ===============================

def visualcrossing(city):

    if not VISUAL_KEY:
        return None

    try:
        r = requests.get(
            f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}",
            params={
                "key": VISUAL_KEY,
                "unitGroup": "metric",
                "include": "current"
            },
            timeout=10
        ).json()


        c = r["currentConditions"]


        return {
            "temp": c["temp"],
            "wind": c["windspeed"],

            "humidity": c["humidity"],
            "uv": c.get("uvindex", 0),
            "precip": c.get("precip", 0),

            "source": "visualcrossing"
        }

    except:
        return None


# ===============================
# LEARNING SYSTEM
# ===============================

def update_weights(real_temp):

    with open(HISTORY_FILE) as f:
        hist = json.load(f)

    if not hist:
        return


    weights = load_weights()

    last = hist[-1]


    for api in last["raw"]:

        src = api["source"]
        predicted = api["temp"]

        error = abs(predicted - real_temp)

        score = max(0.1, 5 - error)

        weights[src] += score * 0.05


    save_weights(weights)


# ===============================
# SMART AI CORE
# ===============================

def smart_weather(city):

    weights = load_weights()


    sources = [
        open_meteo,
        weatherapi,
        visualcrossing
    ]


    results = []


    # Collect API data
    for api in sources:

        d = api(city)

        if d and -60 < d["temp"] < 60:
            results.append(d)


    if not results:
        return None


    # -----------------------
    # Weighted Temperature
    # -----------------------

    total = 0
    wsum = 0

    for r in results:

        w = weights.get(r["source"], 1)

        total += r["temp"] * w
        wsum += w


    final_temp = round(total / wsum, 1)


    # -----------------------
    # Average Sensors
    # -----------------------

    def avg(key):

        vals = [
            r[key] for r in results
            if r.get(key) is not None
        ]

        return round(statistics.mean(vals), 1)


    final_wind = avg("wind")
    final_humidity = avg("humidity")
    final_uv = avg("uv")
    final_precip = avg("precip")


    # -----------------------
    # Confidence
    # -----------------------

    temps = [r["temp"] for r in results]

    spread = max(temps) - min(temps)

    if spread < 2:
        confidence = "High"
    elif spread < 5:
        confidence = "Medium"
    else:
        confidence = "Low"


    # -----------------------
    # Save Learning Data
    # -----------------------

    save_history({
        "time": time.time(),
        "city": city,
        "final": final_temp,
        "raw": results
    })


    # -----------------------
    # Final Package
    # -----------------------

    return {
        "city": city,

        "temperature": final_temp,
        "wind": final_wind,
        "humidity": final_humidity,
        "uv": final_uv,
        "precip": final_precip,

        "confidence": confidence,

        "sources": [r["source"] for r in results],
        "weights": weights
    }