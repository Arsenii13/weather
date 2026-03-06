# ai.py
import api

# -------------------------
# API weights (AI learning later)
# -------------------------

WEIGHTS = {
    "openmeteo": 1.0,
    "weatherapi": 1.0,
    "visual": 1.0
}


# -------------------------
# Helpers
# -------------------------

def _weighted_avg(values, weights):
    """Weighted average supporting numbers OR lists"""

    if not values:
        return None

    # hourly/week (lists)
    if isinstance(values[0], list):

        length = len(values[0])
        result = []

        for i in range(length):

            total = 0
            total_w = 0

            for v, w in zip(values, weights):

                if i < len(v):
                    total += v[i] * w
                    total_w += w

            if total_w == 0:
                result.append(None)
            else:
                result.append(round(total / total_w, 1))

        return result

    # single value
    total = 0
    total_w = 0

    for v, w in zip(values, weights):
        total += v * w
        total_w += w

    if total_w == 0:
        return None

    return round(total / total_w, 1)


def _mix(pack, key):
    """Mix same parameter from multiple APIs"""

    vals = []
    weights = []

    for name, data in pack.items():

        if data is None:
            continue

        if key not in data:
            continue

        vals.append(data[key])
        weights.append(WEIGHTS.get(name, 1))

    if not vals:
        return None

    return _weighted_avg(vals, weights)


# -------------------------
# CURRENT WEATHER
# -------------------------

def smart_current(city):

    pack = api.get_all_current(city)

    return {
        "temp": _mix(pack, "temp"),
        "wind": _mix(pack, "wind"),
        "humidity": _mix(pack, "humidity"),
        "code": _mix(pack, "code")
    }


# -------------------------
# HOURLY WEATHER
# -------------------------

def smart_hourly(city):

    pack = api.get_all_hourly(city)

    return {
        "temp": _mix(pack, "temp"),
        "wind": _mix(pack, "wind"),
        "humidity": _mix(pack, "humidity"),
        "code": _mix(pack, "code"),
        "time": pack["openmeteo"]["time"] if pack["openmeteo"] else []
    }


# -------------------------
# TOMORROW WEATHER
# -------------------------

def smart_tomorrow(city):

    pack = api.get_all_tomorrow(city)

    return {
        "temp_min": _mix(pack, "temp_min"),
        "temp_max": _mix(pack, "temp_max"),
        "wind": _mix(pack, "wind"),
        "humidity": _mix(pack, "humidity"),
        "code": _mix(pack, "code")
    }


# -------------------------
# WEEK WEATHER
# -------------------------

def smart_week(city):

    pack = api.get_all_week(city)

    return {
        "temp_min": _mix(pack, "temp_min"),
        "temp_max": _mix(pack, "temp_max"),
        "wind": _mix(pack, "wind"),
        "humidity": _mix(pack, "humidity"),
        "code": _mix(pack, "code"),
        "days": pack["openmeteo"]["days"] if pack["openmeteo"] else []
    }