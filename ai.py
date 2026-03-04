# ai.py

import api
import json
import os
import statistics


# =============================
# CONFIG
# =============================

WEIGHT_FILE = "ai_weights.json"

DEFAULT_WEIGHTS = {
    "openmeteo": 1.0,
    "weatherapi": 1.0,
    "visual": 1.0
}


# =============================
# LOAD / SAVE LEARNING
# =============================

def load_weights():

    if not os.path.exists(WEIGHT_FILE):
        return DEFAULT_WEIGHTS.copy()

    with open(WEIGHT_FILE, "r") as f:
        return json.load(f)


def save_weights(w):

    with open(WEIGHT_FILE, "w") as f:
        json.dump(w, f, indent=2)


# =============================
# CLEAN DATA
# =============================

def _filter(values):

    return [v for v in values if v is not None]


def _weighted_avg(values, weights):

    total = 0
    wsum = 0

    for v, w in zip(values, weights):

        if v is None:
            continue

        total += v * w
        wsum += w


    if wsum == 0:
        return None

    return round(total / wsum, 2)


# =============================
# CONFIDENCE
# =============================

def _confidence(values):

    clean = _filter(values)

    if len(clean) <= 1:
        return "Low"

    std = statistics.stdev(clean)

    if std < 0.8:
        return "High"

    if std < 2:
        return "Medium"

    return "Low"


# =============================
# CORE MIXER
# =============================

def _mix(data, field):

    w = load_weights()

    vals = [
        data["openmeteo"].get(field),
        data["weatherapi"].get(field),
        data["visual"].get(field)
    ]

    weights = [
        w["openmeteo"],
        w["weatherapi"],
        w["visual"]
    ]


    return (
        _weighted_avg(vals, weights),
        _confidence(vals)
    )


# =============================
# AUTO LEARNING
# =============================

def _learn(data, real):

    w = load_weights()

    for src in w:

        if src in data and data[src]["temp"]:

            err = abs(data[src]["temp"] - real)

            if err < 1:
                w[src] += 0.05
            else:
                w[src] -= 0.05


    save_weights(w)


# =============================
# CURRENT
# =============================

def smart_current(city):

    raw = api.get_all_current(city)

    if not raw:
        return None


    temp, conf = _mix(raw, "temp")
    wind, _ = _mix(raw, "wind")
    hum, _ = _mix(raw, "humidity")
    uv, _ = _mix(raw, "uv")
    rain, _ = _mix(raw, "precip")
    code, _ = _mix(raw, "code")


    return {
        "city": city,

        "temperature": temp,
        "wind": wind,
        "humidity": hum,

        "uv": uv,
        "precip": rain,
        "code": int(code) if code else 0,

        "confidence": conf
    }


# =============================
# HOURLY
# =============================

def smart_hourly(city):

    raw = api.get_all_hourly(city)

    if not raw:
        return None


    hours = []


    for i in range(24):

        pack = {
            "openmeteo": raw["openmeteo"][i],
            "weatherapi": raw["weatherapi"][i],
            "visual": raw["visual"][i]
        }


        temp, _ = _mix(pack, "temp")
        hum, _ = _mix(pack, "humidity")
        rain, _ = _mix(pack, "precip")
        code, _ = _mix(pack, "code")


        hours.append({
            "time": pack["openmeteo"]["time"],

            "temp": temp,
            "humidity": hum,
            "precip": rain,
            "code": int(code) if code else 0
        })


    return hours


# =============================
# TOMORROW
# =============================

def smart_tomorrow(city):

    raw = api.get_all_tomorrow(city)

    if not raw:
        return None


    temp_max, _ = _mix(raw, "max")
    temp_min, _ = _mix(raw, "min")
    uv, _ = _mix(raw, "uv")
    rain, _ = _mix(raw, "precip")
    code, _ = _mix(raw, "code")


    return {
        "date": raw["openmeteo"]["date"],

        "max": temp_max,
        "min": temp_min,

        "uv": uv,
        "precip": rain,

        "code": int(code) if code else 0
    }


# =============================
# WEEK
# =============================

def smart_week(city):

    raw = api.get_all_week(city)

    if not raw:
        return None


    result = []


    for i in range(len(raw["openmeteo"])):

        pack = {
            "openmeteo": raw["openmeteo"][i],
            "weatherapi": raw["weatherapi"][i],
            "visual": raw["visual"][i]
        }


        max_t, _ = _mix(pack, "max")
        min_t, _ = _mix(pack, "min")
        uv, _ = _mix(pack, "uv")
        rain, _ = _mix(pack, "precip")
        code, _ = _mix(pack, "code")


        result.append({
            "date": pack["openmeteo"]["date"],

            "max": max_t,
            "min": min_t,

            "uv": uv,
            "precip": rain,

            "code": int(code) if code else 0
        })


    return result