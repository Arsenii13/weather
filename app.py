import weather
import file
import graph


# =============================
# Help
# =============================
def show_help():

    print("""
📖 COMMANDS

help

weather <city>
weather <city> by hours

tomorrow <city>
forecast <city>

save day <city> as <file>
save day <city> by hours as <file>
save week <city> as <file>

open <file>
delete <file>
replace <file>

graph <file>

exit
""")


# =============================
# Main App
# =============================
def main():

    print("🌦️ Weather Assistant")
    print("Type: help\n")


    while True:

        cmd = input("> ").strip()
        low = cmd.lower()


        # Exit
        if low == "exit":
            print("Bye 👋")
            break


        # Help
        elif low == "help":
            show_help()


        # Weather
        elif low.startswith("weather "):

            if " by hours" in low:

                city = cmd[8:].replace("by hours", "").strip()

                lines = weather.get_weather_lines(
                    city, "day", True
                )

            else:

                city = cmd[8:].strip()

                lines = weather.get_weather_lines(
                    city, "day"
                )


            if lines is None:
                print("❌ City not found\n")
            else:
                print()
                for l in lines:
                    print(l)
                print()


        # Tomorrow
        elif low.startswith("tomorrow "):

            city = cmd[9:].strip()

            lines = weather.get_weather_lines(
                city, "tomorrow"
            )

            if lines is None:
                print("❌ City not found\n")
            else:
                print()
                for l in lines:
                    print(l)
                print()


        # Forecast
        elif low.startswith("forecast "):

            city = cmd[9:].strip()

            lines = weather.get_weather_lines(
                city, "week"
            )

            if lines is None:
                print("❌ City not found\n")
            else:
                print()
                for l in lines:
                    print(l)
                print()


        # Save
        elif low.startswith("save "):

            data = file.parse_save_command(cmd)

            if data is None:
                print("❌ Format: save day/week <city> [by hours] as <file>\n")
                continue


            lines = weather.get_weather_lines(
                data["city"],
                data["mode"],
                data["by_hours"]
            )


            if lines is None:
                print("❌ City not found\n")
                continue


            header = f"{data['city']} {data['mode']}"

            file.save(
                data["filename"],
                header,
                lines
            )


        # Open file
        elif low.startswith("open "):

            filename = cmd[5:].strip()

            file.open_file(filename)


        # Delete file
        elif low.startswith("delete "):

            filename = cmd[7:].strip()

            file.delete(filename)


        # Replace file
        elif low.startswith("replace "):

            filename = cmd[8:].strip()


            print("✏️ Enter new content (finish with empty line):")

            lines = []

            while True:

                line = input()

                if line == "":
                    break

                lines.append(line)


            file.replace(
                filename,
                "MANUAL REPLACE",
                lines
            )


        # Graph
        elif low.startswith("graph "):

            filename = cmd[6:].strip()

            graph.draw(filename)


        # Unknown
        else:

            print("❌ Unknown command (type help)\n")



# =============================
# Run
# =============================
if __name__ == "__main__":
    main()
