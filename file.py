import os
from datetime import datetime


# =============================
# Save (Append)
# =============================
def save(filename, header, lines):

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    with open(filename, "a", encoding="utf-8") as f:

        f.write(f"\n=== {now} | {header} ===\n")

        for line in lines:
            f.write(line + "\n")


    print(f"💾 Saved to {filename}\n")


# =============================
# Replace (Overwrite)
# =============================
def replace(filename, header, lines):

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    with open(filename, "w", encoding="utf-8") as f:

        f.write(f"=== {now} | {header} ===\n")

        for line in lines:
            f.write(line + "\n")


    print(f"✏️ Replaced content in {filename}\n")


# =============================
# Open (Print File)
# =============================
def open_file(filename):

    if not os.path.exists(filename):
        print("❌ File not found\n")
        return


    print(f"\n📂 {filename}\n")

    with open(filename, "r", encoding="utf-8") as f:

        print(f.read())

    print()


# =============================
# Delete
# =============================
def delete(filename):

    if not os.path.exists(filename):
        print("❌ File not found\n")
        return


    os.remove(filename)

    print(f"🗑️ Deleted {filename}\n")


# =============================
# Parse Save Command
# =============================
def parse_save_command(cmd):
    """
    Supports:

    save day varna as file.txt
    save day varna by hours as file.txt
    save week sofia as data.txt
    """

    parts = cmd.lower().split()

    if "as" not in parts:
        return None


    try:

        mode = parts[1]        # day / week
        city = parts[2]        # city

        by_hours = False

        if "by" in parts and "hours" in parts:
            by_hours = True

        filename = cmd.split("as")[-1].strip()

        return {
            "mode": mode,
            "city": city,
            "by_hours": by_hours,
            "filename": filename
        }

    except:
        return None
