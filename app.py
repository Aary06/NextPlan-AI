import streamlit as st
import json
import os
from weekly_engine import build_week_grid
from allocation_engine import allocate_tasks

DATA_PATH = "data/user_data.json"

st.set_page_config(page_title="NextPlan-AI", layout="centered")

# --------- Dark Theme ----------
st.markdown("""
<style>
body {
    background-color: #0E1117;
    color: white;
}
.stButton>button {
    background-color: #1F6FEB;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)


# --------- Load / Save ----------
def load_data():
    if not os.path.exists(DATA_PATH):
        return {
            "profile": {
                "wake_time": "",
                "sleep_time": "",
                "fixed_commitments": [],
                "tasks": []
            },
            "history": {}
        }
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)


def mark_task_complete(data, day, start, task_name, completed):
    if day not in data["history"]:
        data["history"][day] = {}

    key = f"{start}_{task_name}"
    data["history"][day][key] = completed


data = load_data()

st.title("🚀 NextPlan-AI")
st.subheader("Adaptive Weekly Intelligence Planner")

# --------- Workflow Setup ----------
st.header("🔧 Setup Your Workflow")

wake_time = st.time_input("Wake Time")
sleep_time = st.time_input("Sleep Time")

st.subheader("Add Fixed Commitments")
commitments = []
num_commitments = st.number_input("How many fixed commitments?", 0, 5, 0)

for i in range(num_commitments):
    st.write(f"Commitment {i+1}")
    name = st.text_input(f"Name {i}", key=f"name_{i}")
    start = st.time_input(f"Start {i}", key=f"start_{i}")
    end = st.time_input(f"End {i}", key=f"end_{i}")

    commitments.append({
        "name": name,
        "start": start.strftime("%H:%M"),
        "end": end.strftime("%H:%M")
    })

st.subheader("Add Custom Tasks")
tasks = []
num_tasks = st.number_input("Number of tasks", 1, 10, 1)

for i in range(num_tasks):
    name = st.text_input(f"Task Name {i}", key=f"task_{i}")
    weekly_hours = st.number_input(
        f"Weekly Target Hours {i}", 1, 50, 7, key=f"hours_{i}"
    )

    tasks.append({
        "name": name,
        "weekly_target_hours": weekly_hours
    })

if st.button("Save / Update Profile"):
    data["profile"]["wake_time"] = wake_time.strftime("%H:%M")
    data["profile"]["sleep_time"] = sleep_time.strftime("%H:%M")
    data["profile"]["fixed_commitments"] = commitments
    data["profile"]["tasks"] = tasks
    save_data(data)
    st.success("Profile Saved Successfully!")


# --------- Weekly Planner ----------
if data["profile"]["tasks"]:

    st.header("📅 Weekly Smart Plan")

    week = build_week_grid(data["profile"])
    week = allocate_tasks(week, data["profile"])

    selected_day = st.selectbox("Select Day", list(week.keys()))
    blocks = week[selected_day]

    # --------- Merge Consecutive Blocks ----------
    merged_schedule = []
    current_task = None
    current_type = None
    start_time = None

    for block in blocks:
        if block["type"] != current_type or block["task"] != current_task:
            if current_type is not None:
                merged_schedule.append({
                    "start": start_time,
                    "end": block["start"],
                    "type": current_type,
                    "task": current_task
                })
            current_type = block["type"]
            current_task = block["task"]
            start_time = block["start"]

    if current_type is not None:
        merged_schedule.append({
            "start": start_time,
            "end": blocks[-1]["end"],
            "type": current_type,
            "task": current_task
        })

    st.subheader(f"📅 {selected_day} Plan")

    total_task_minutes = 0
    evening_load = 0
    morning_heavy = False

    for item in merged_schedule:

        # -------- TASKS (checkbox) --------
        if item["type"] == "task" and item["task"]:

            key_id = f"{selected_day}_{item['start']}_{item['task']}"

            completed = False
            if selected_day in data["history"]:
                completed = data["history"][selected_day].get(
                    f"{item['start']}_{item['task']}", False
                )

            checked = st.checkbox(
                f"{item['start']} - {item['end']} → {item['task']}",
                value=completed,
                key=key_id
            )

            mark_task_complete(
                data,
                selected_day,
                item["start"],
                item["task"],
                checked
            )

            # AI Metrics
            start_hour = int(item["start"].split(":")[0])
            end_hour = int(item["end"].split(":")[0])
            duration = (end_hour - start_hour) * 60
            total_task_minutes += duration

            if 6 <= start_hour <= 9 and "DSA" in item["task"]:
                morning_heavy = True

            if start_hour >= 21:
                evening_load += duration

        # -------- FIXED COMMITMENTS --------
        elif item["type"] == "fixed" and item["task"]:
            st.write(f"{item['start']} - {item['end']} → {item['task']}")

        # -------- IGNORE FREE TIME --------
        else:
            continue

    save_data(data)

    # --------- AI Suggestions ----------
    st.markdown("---")
    st.subheader("🧠 AI Suggestions")

    suggestions = []

    if not morning_heavy:
        suggestions.append("Consider placing heavy tasks like DSA in early morning for maximum focus.")

    if total_task_minutes > 360:
        suggestions.append("Your study load today exceeds 6 hours. Risk of burnout.")

    if evening_load > 120:
        suggestions.append("Evening workload is high. Consider lighter tasks before sleep.")

    if selected_day in ["Saturday", "Sunday"] and total_task_minutes > 240:
        suggestions.append("Weekend seems heavy. You may want lighter cognitive load.")

    if suggestions:
        for s in suggestions:
            st.info(s)
    else:
        st.success("Your schedule looks well balanced today. Great job!")