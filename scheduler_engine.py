from datetime import datetime, timedelta

def generate_schedule(profile):
    if not profile["wake_time"] or not profile["sleep_time"]:
        return []

    wake = datetime.strptime(profile["wake_time"], "%H:%M")
    sleep = datetime.strptime(profile["sleep_time"], "%H:%M")

    fixed_blocks = profile["fixed_commitments"]

    fixed_ranges = []
    for block in fixed_blocks:
        start = datetime.strptime(block["start"], "%H:%M")
        end = datetime.strptime(block["end"], "%H:%M")
        fixed_ranges.append((start, end))

    fixed_ranges.sort()

    free_slots = []
    current = wake

    for start, end in fixed_ranges:
        if current < start:
            free_slots.append((current, start))
        current = end

    if current < sleep:
        free_slots.append((current, sleep))

    schedule = []

    for task in profile["tasks"]:
        daily_hours = task["weekly_target_hours"] / 7
        task_duration = timedelta(hours=daily_hours)

        for i, (slot_start, slot_end) in enumerate(free_slots):
            slot_duration = slot_end - slot_start

            if slot_duration >= task_duration:
                task_start = slot_start
                task_end = slot_start + task_duration

                schedule.append({
                    "task": task["name"],
                    "start": task_start.strftime("%H:%M"),
                    "end": task_end.strftime("%H:%M")
                })

                free_slots[i] = (task_end, slot_end)
                break

    return schedule