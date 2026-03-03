def allocate_tasks(week, profile):
    tasks = profile["tasks"]

    # Convert weekly hours to total 30-min blocks
    task_requirements = {}
    for task in tasks:
        total_blocks = int((task["weekly_target_hours"] * 60) / 30)
        task_requirements[task["name"]] = total_blocks

    for day, blocks in week.items():

        weekend_multiplier = 0.7 if day in ["Saturday", "Sunday"] else 1.0

        for task in tasks:

            remaining = task_requirements[task["name"]]
            if remaining <= 0:
                continue

            daily_blocks = int((remaining / 7) * weekend_multiplier)
            if daily_blocks <= 0:
                continue

            consecutive = 0
            start_index = None

            for i in range(len(blocks)):

                if blocks[i]["type"] == "free":

                    if consecutive == 0:
                        start_index = i

                    consecutive += 1

                    if consecutive == daily_blocks:

                        # Assign continuous chunk
                        for j in range(start_index, start_index + daily_blocks):
                            blocks[j]["type"] = "task"
                            blocks[j]["task"] = task["name"]

                        task_requirements[task["name"]] -= daily_blocks
                        break
                else:
                    consecutive = 0

    return week