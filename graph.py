import plotly.graph_objects as go
import os


# =============================
# Parse Weather File
# =============================
def parse_file(filename):

    if not os.path.exists(filename):
        return None


    dates = []
    max_t = []
    min_t = []
    current_t = []


    with open(filename, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            # Skip headers
            if line.startswith("===") or not line:
                continue


            # WEEK FORMAT:
            # 2026-03-01 | Sunny | 12/4 °C

            if "/" in line and "|" in line:

                parts = line.split("|")

                if len(parts) < 3:
                    continue

                date = parts[0].strip()

                temps = parts[2].replace("°C", "").replace("C", "").strip()

                if "/" not in temps:
                    continue

                t1, t2 = temps.split("/")

                try:
                    dates.append(date)
                    max_t.append(float(t1))
                    min_t.append(float(t2))
                except:
                    pass


            # DAY FORMAT:
            # Temperature: 12 °C

            elif "Temperature" in line:

                try:
                    temp = line.split(":")[1].replace("°C", "").strip()
                    current_t.append(float(temp))
                except:
                    pass


    return {
        "dates": dates,
        "max": max_t,
        "min": min_t,
        "current": current_t
    }


# =============================
# Draw Graph
# =============================
def draw(filename):

    data = parse_file(filename)

    if data is None:
        print("❌ File not found\n")
        return


    has_week = len(data["dates"]) > 0
    has_day = len(data["current"]) > 0


    if not has_week and not has_day:
        print("❌ No graph data in file\n")
        return


    fig = go.Figure()


    # WEEK GRAPH
    if has_week:

        fig.add_trace(go.Scatter(
            x=data["dates"],
            y=data["max"],
            mode="lines+markers",
            name="Max Temp"
        ))


        fig.add_trace(go.Scatter(
            x=data["dates"],
            y=data["min"],
            mode="lines+markers",
            name="Min Temp"
        ))


    # DAY GRAPH
    if has_day:

        fig.add_trace(go.Scatter(
            y=data["current"],
            mode="lines+markers",
            name="Current Temp"
        ))


    fig.update_layout(
        title=f"Weather Graph: {filename}",
        xaxis_title="Date / Index",
        yaxis_title="Temperature (°C)",
        hovermode="x unified"
    )


    fig.show()
