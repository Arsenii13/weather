import requests
import statistics
import os
import json
import time


# ===============================
# CONFIG
# ===============================

WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")
VISUAL_KEY = os.getenv("VISUAL_KEY")

HISTORY_FILE = "weather_history.json"
WEIGHTS_FILE = "api_weights.json"


# ===============================
# INIT FILES
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
            json.dump(weights, f)


init_files()


# ===============================
# HELPERS
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
# API FUNCTIONS
# ===============================

def open_meteo(city):
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=10
        ).json()

        if "results" not in geo:
            return None

        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]

        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": True
            },
            timeout=10
        ).json()

        w = r["current_weather"]

        return {
    "temp": w["temperature"],
    "wind": w["windspeed"],
    "source": "open-meteo",

    "humidity": r["hourly"]["relativehumidity_2m"][0],
    "precip": r["hourly"]["precipitation"][0],
    "uv": r["daily"]["uv_index_max"][0]
}

    except:
        return None


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

        return {
            "temp": r["current"]["temp_c"],
            "source": "weatherapi"
        }

    except:
        return None


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

        return {
            "temp": r["currentConditions"]["temp"],
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

    weights = load_weights()

    # Take last entry
    last = hist[-1]

    for api in last["raw"]:

        src = api["source"]
        predicted = api["temp"]

        error = abs(predicted - real_temp)

        # Smaller error = better weight
        score = max(0.1, 5 - error)

        weights[src] += score * 0.05

    save_weights(weights)


# ===============================
# SMART AI
# ===============================

def smart_weather(city):

    weights = load_weights()

    sources = [
        open_meteo,
        weatherapi,
        visualcrossing
    ]

    results = []

    for api in sources:
        d = api(city)

        if d and -60 < d["temp"] < 60:
            results.append(d)

    if not results:
        return None


    # -----------------------
    # WEIGHTED AI AVERAGE
    # -----------------------

    total = 0
    weight_sum = 0

    for r in results:

        w = weights.get(r["source"], 1)

        total += r["temp"] * w
        weight_sum += w


    final_temp = round(total / weight_sum, 1)


    # -----------------------
    # CONFIDENCE
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
    # SAVE DATA FOR LEARNING
    # -----------------------

    save_history({
        "time": time.time(),
        "city": city,
        "final": final_temp,
        "raw": results
    })


    return {
        "city": city,
        "temperature": final_temp,
        "confidence": confidence,
        "sources": [r["source"] for r in results],
        "weights": weights
    }