from flask import Flask, render_template, request
import weather


app = Flask(__name__)
app.secret_key = 'coolkey'  # Replace with a secure key

@app.route("/", methods=["GET", "POST"])
def index():

    result = None
    city = ""
    graph_data = None

    # Inside your index() function, before POST request handling
    if 'history' not in session:
        session['history'] = []

# After getting city from form
    if city and city not in session['history']:
        session['history'].append(city)
    # Optional: limit history length
        session['history'] = session['history'][-10:]
    if request.method == "POST":

        city = request.form.get("city")
        mode = request.form.get("mode")


        # Text result
        if mode == "now":
            result = weather.get_weather_lines(city, "day")

        elif mode == "hourly":
            result = weather.get_weather_lines(city, "day", True)

        elif mode == "tomorrow":
            result = weather.get_weather_lines(city, "tomorrow")

        elif mode == "week":
            result = weather.get_weather_lines(city, "week")


            # Prepare graph data
            daily = weather.get_daily(city)

            if daily:

                graph_data = {
                    "dates": daily["time"],
                    "max": daily["temperature_2m_max"],
                    "min": daily["temperature_2m_min"]
                }


        if result is None:
            result = ["❌ City not found"]


    return render_template(
        "index.html",
        result=result,
        city=city,
        graph_data=graph_data,
        history=session['history']
    )



import os

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
