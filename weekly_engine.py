from datetime import datetime, timedelta

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def generate_time_blocks(wake_time, sleep_time):
    blocks = []
    current = datetime.strptime(wake_time, "%H:%M")
    sleep = datetime.strptime(sleep_time, "%H:%M")

    while current < sleep:
        end = current + timedelta(minutes=30)
        blocks.append({
            "start": current.strftime("%H:%M"),
            "end": end.strftime("%H:%M"),
            "type": "free",
            "task": None
        })
        current = end

    return blocks


def build_week_grid(profile):
    week = {}

    for day in DAYS:
        blocks = generate_time_blocks(profile["wake_time"], profile["sleep_time"])

        # Mark fixed commitments
        for commitment in profile["fixed_commitments"]:
            start = commitment["start"]
            end = commitment["end"]

            for block in blocks:
                if block["start"] >= start and block["end"] <= end:
                    block["type"] = "fixed"
                    block["task"] = commitment["name"]

        week[day] = blocks

    return week