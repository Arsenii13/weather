import requests


# =============================
# Weather Codes
# =============================
WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),

    45: ("Fog", "🌫️"),
    48: ("Rime fog", "🌫️"),

    51: ("Light drizzle", "🌦️"),
    53: ("Drizzle", "🌦️"),
    55: ("Heavy drizzle", "🌧️"),

    61: ("Light rain", "🌧️"),
    63: ("Rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),

    71: ("Light snow", "❄️"),
    73: ("Snow", "❄️"),
    75: ("Heavy snow", "❄️"),

    80: ("Rain showers", "🌦️"),
    81: ("Heavy showers", "🌧️"),

    95: ("Thunderstorm", "⛈️")
}


# =============================
# Decode Code
# =============================
def decode_weather(code):

    return WEATHER_CODES.get(code, ("Unknown", "❓"))


# =============================
# Get City Coordinates
# =============================
def get_coordinates(city):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 1,
        "language": "en"
    }

    r = requests.get(url, params=params).json()

    if "results" not in r:
        return None, None

    res = r["results"][0]

    return res["latitude"], res["longitude"]


# =============================
# Get Current Weather
# =============================
def get_current(city):

    lat, lon = get_coordinates(city)

    if lat is None:
        return None


    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "auto"
    }

    data = requests.get(url, params=params).json()

    return data["current_weather"]


# =============================
# Get Hourly
# =============================
def get_hourly(city):

    lat, lon = get_coordinates(city)

    if lat is None:
        return None


    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,

        "hourly": [
            "temperature_2m",
            "weathercode"
        ],

        "timezone": "auto"
    }

    data = requests.get(url, params=params).json()

    return data["hourly"]


# =============================
# Get Daily
# =============================
def get_daily(city):

    lat, lon = get_coordinates(city)

    if lat is None:
        return None


    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,

        "daily": [
            "weathercode",
            "temperature_2m_max",
            "temperature_2m_min"
        ],

        "timezone": "auto"
    }

    data = requests.get(url, params=params).json()

    return data["daily"]


# =============================
# Format Current
# =============================
def format_current(city):

    data = get_current(city)

    if data is None:
        return None


    text, emoji = decode_weather(data["weathercode"])


    lines = [
        f"City: {city}",
        f"{emoji} {text}",
        f"Temperature: {data['temperature']} °C",
        f"Wind: {data['windspeed']} km/h"
    ]


    return lines


# =============================
# Format Hourly (24h)
# =============================
def format_hourly(city):

    data = get_hourly(city)

    if data is None:
        return None


    lines = [f"Hourly forecast for {city}:"]


    for i in range(24):

        time = data["time"][i].split("T")[1]
        temp = data["temperature_2m"][i]
        code = data["weathercode"][i]

        text, emoji = decode_weather(code)

        line = f"{time} | {emoji} {text} | {temp} °C"

        lines.append(line)


    return lines


# =============================
# Format Tomorrow
# =============================
def format_tomorrow(city):

    data = get_daily(city)

    if data is None:
        return None


    code = data["weathercode"][1]
    max_t = data["temperature_2m_max"][1]
    min_t = data["temperature_2m_min"][1]
    date = data["time"][1]

    text, emoji = decode_weather(code)


    lines = [
        f"Tomorrow in {city} ({date})",
        f"{emoji} {text}",
        f"Max: {max_t} °C",
        f"Min: {min_t} °C"
    ]


    return lines


# =============================
# Format Week
# =============================
def format_week(city):

    data = get_daily(city)

    if data is None:
        return None


    lines = [f"7-Day forecast for {city}:"]


    for i in range(len(data["time"])):

        date = data["time"][i]
        code = data["weathercode"][i]
        max_t = data["temperature_2m_max"][i]
        min_t = data["temperature_2m_min"][i]

        text, emoji = decode_weather(code)

        line = f"{date} | {emoji} {text} | {max_t}/{min_t} °C"

        lines.append(line)


    return lines


# =============================
# Universal Getter
# =============================
def get_weather_lines(city, mode, by_hours=False):

    """
    mode: day / week / tomorrow / now
    """

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

    else:
        return None
