"""Parse user-entered bike share details. Invalid input returns None."""

import re


def parse_ride_duration(text):
    """Convert hours and two-digit minutes to a total minute count."""
    if not isinstance(text, str):
        return None
    match = re.fullmatch(r"([0-9]{2,}):([0-5][0-9])", text.strip())
    if match is None:
        return None
    try:
        hours, minutes = map(int, match.groups())
    except ValueError:
        return None
    return hours * 60 + minutes


def format_station_code(code):
    """Format an ASCII zone letter and station number, preserving leading zeros."""
    if not isinstance(code, str):
        return None
    match = re.fullmatch(r"([A-Za-z])([0-9]+)", code.strip())
    if match is None:
        return None
    zone, number = match.groups()
    return f"{zone.upper()}-{number}"


def parse_ride_log(line):
    """Parse a known bike type, positive minute count and yes/no flag."""
    if not isinstance(line, str):
        return None
    fields = [field.strip() for field in line.split(",")]
    if len(fields) != 3:
        return None
    bike_type, minutes, subscriber = fields
    if bike_type not in {"standard", "electric", "cargo"}:
        return None
    if subscriber not in {"yes", "no"} or not re.fullmatch(r"[0-9]+", minutes):
        return None
    try:
        duration = int(minutes)
    except ValueError:
        return None
    if duration <= 0:
        return None
    return bike_type, duration, subscriber == "yes"


def main():
    """Run the three parser demonstrations."""
    prompts = (
        ("ride duration (HH:MM)", "Duration in minutes", parse_ride_duration),
        ("station code (e.g. a12)", "Formatted station code", format_station_code),
        ("ride log (type,minutes,subscriber)", "Parsed ride log", parse_ride_log),
    )
    for prompt, label, parser in prompts:
        try:
            value = input(f"Enter {prompt}: ")
        except EOFError:
            return
        result = parser(value)
        print(f"{label}: {result if result is not None else 'Invalid input'}")


if __name__ == "__main__":
    main()
