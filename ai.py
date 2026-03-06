# ai.py

import api


# =============================
# TRUST WEIGHTS
# =============================

WEIGHTS = {
    "openmeteo": 1.0,
    "weatherapi": 1.0,
    "visual": 1.0
}


# =============================
# NUMERIC MIXING
# =============================

def _weighted_avg(values, weights):

    total = 0
    wsum = 0

    for v, w in zip(values, weights):

        if v is None:
            continue

        total += float(v) * w
        wsum += w

    if wsum == 0:
        return None

    return round(total / wsum, 2)


# =============================
# VOTE FOR WEATHER CODE
# =============================

def _vote(values, weights):

    scores = {}

    for v, w in zip(values, weights):

        if v is None:
            continue

        scores[v] = scores.get(v, 0) + w

    if not scores:
        return None

    return max(scores, key=scores.get)


# =============================
# MIX ONE FIELD
# =============================

def _mix(pack, key):

    vals = []
    weights = []

    for name, data in pack.items():

        if not data:
            continue

        if key not in data:
            continue

        vals.append(data[key])
        weights.append(WEIGHTS.get(name, 1))

    if not vals:
        return None

    if key == "code":
        return _vote(vals, weights)

    return _weighted_avg(vals, weights)


# =============================
# CURRENT WEATHER AI
# =============================

def smart_current(city):

    pack = api.get_all_current(city)

    return {
        "city": city, 
        "temp": _mix(pack, "temp"),
        "wind": _mix(pack, "wind"),
        "humidity": _mix(pack, "humidity"),
        "precip": _mix(pack, "precip"),
        "uv": _mix(pack, "uv"),

        "code": _mix(pack, "code")

    }


# =============================
# HOURLY AI
# =============================

def smart_hourly(city):

    pack = api.get_all_hourly(city)

    result = []

    for i in range(24):

        hour_pack = {}

        for name, data in pack.items():

            if not data:
                continue

            if i >= len(data):
                continue

            hour_pack[name] = data[i]

        result.append({
            
            "time": _mix(hour_pack, "time"),
            "temp": _mix(hour_pack, "temp"),
            "humidity": _mix(hour_pack, "humidity"),
            "precip": _mix(hour_pack, "precip"),
            "code": _mix(hour_pack, "code")

        })

    return result


# =============================
# TOMORROW AI
# =============================

def smart_tomorrow(city):

    pack = api.get_all_tomorrow(city)

    return {

        "date": _mix(pack, "date"),

        "max": _mix(pack, "max"),
        "min": _mix(pack, "min"),

        "uv": _mix(pack, "uv"),
        "precip": _mix(pack, "precip"),

        "code": _mix(pack, "code")

    }


# =============================
# WEEK AI
# =============================

def smart_week(city):

    pack = api.get_all_week(city)

    result = []

    for i in range(7):

        day_pack = {}

        for name, data in pack.items():

            if not data:
                continue

            if i >= len(data):
                continue

            day_pack[name] = data[i]

        result.append({

            "date": _mix(day_pack, "date"),

            "max": _mix(day_pack, "max"),
            "min": _mix(day_pack, "min"),

            "uv": _mix(day_pack, "uv"),
            "precip": _mix(day_pack, "precip"),

            "code": _mix(day_pack, "code")

        })

    return result