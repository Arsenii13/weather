# weather.py

import ai


# =============================
# WEATHER CODES (Open-Meteo)
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


def decode(code):

    return WEATHER_CODES.get(code, ("Unknown", "❓"))


# =============================
# CURRENT (AI)
# =============================

def current(city):

    data = ai.smart_current(city)

    if not data:
        return None


    lines = [
        f"📍 {data['city']}",

        f"🌡️ Temperature: {data['temperature']} °C",
        f"💨 Wind: {data['wind']} km/h",

        f"💧 Humidity: {data['humidity']} %",
        f"☀️ UV Index: {data['uv']}",

        f"🌧️ Precipitation: {data['precip']} mm",

        f"🤖 Confidence: {data['confidence']}"
    ]


    return lines


# =============================
# HOURLY (AI)
# =============================

def hourly(city):

    data = ai.smart_hourly(city)

    if not data:
        return None


    lines = [f"Hourly forecast for {city}:"]


    for h in data:

        text, em = decode(h["code"])

        line = (
            f"{h['time']} | "
            f"{em} {text} | "
            f"{h['temp']}°C | "
            f"💧{h['humidity']}% | "
            f"🌧️{h['precip']}mm"
        )

        lines.append(line)


    return lines


# =============================
# TOMORROW (AI)
# =============================

def tomorrow(city):

    d = ai.smart_tomorrow(city)

    if not d:
        return None


    text, em = decode(d["code"])


    return [
        f"Tomorrow in {city} ({d['date']})",

        f"{em} {text}",

        f"🌡️ {d['max']} / {d['min']} °C",

        f"☀️ UV: {d['uv']}",
        f"🌧️ Rain: {d['precip']} mm"
    ]


# =============================
# WEEK (AI)
# =============================

def week(city):

    data = ai.smart_week(city)

    if not data:
        return None


    lines = [f"7-Day Forecast for {city}:"]


    for d in data:

        text, em = decode(d["code"])

        line = (
            f"{d['date']} | "
            f"{em} {text} | "
            f"{d['max']}/{d['min']}°C | "
            f"☀️UV {d['uv']} | "
            f"🌧️{d['precip']}mm"
        )

        lines.append(line)


    return lines


# =============================
# UNIVERSAL ENTRY
# =============================

def get_weather_lines(city, mode, by_hours=False):

    if mode == "now":
        return current(city)

    if mode == "day":

        if by_hours:
            return hourly(city)

        return current(city)

    if mode == "tomorrow":
        return tomorrow(city)

    if mode == "week":
        return week(city)

    return None