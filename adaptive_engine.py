def adjust_targets(profile, history):
    task_stats = {}

    for day in history:
        for task in day["tasks"]:
            name = task["name"]
            completed = task["completed"]

            if name not in task_stats:
                task_stats[name] = {"done": 0, "total": 0}

            task_stats[name]["total"] += 1
            if completed:
                task_stats[name]["done"] += 1

    for task in profile["tasks"]:
        name = task["name"]
        if name in task_stats:
            success_rate = task_stats[name]["done"] / task_stats[name]["total"]

            # If success rate low, reduce load
            if success_rate < 0.5:
                task["weekly_target_hours"] *= 0.9

            # If very consistent, increase difficulty
            elif success_rate > 0.8:
                task["weekly_target_hours"] *= 1.05

    return profile