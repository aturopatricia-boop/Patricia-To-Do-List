from flask import Flask, render_template, request, redirect
from supabase import create_client
from dotenv import load_dotenv
import os
import reminder


load_dotenv()


app = Flask(__name__)


# ==============================
# SUPABASE CONFIGURATION
# ==============================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL is missing from the .env file"
    )


if not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_KEY is missing from the .env file"
    )


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ==============================
# DASHBOARD
# ==============================

@app.route("/")
def dashboard():

    # ==========================
    # GET TASKS
    # ==========================

    tasks_response = (
        supabase
        .table("tasks")
        .select("*")
        .order("task_date")
        .order("task_time")
        .execute()
    )

    tasks = tasks_response.data


    # ==========================
    # GET EVENTS
    # ==========================

    events_response = (
        supabase
        .table("events")
        .select("*")
        .order("event_date")
        .order("event_time")
        .execute()
    )

    events = events_response.data


    # ==========================
    # GET GOALS
    # ==========================

    goals_response = (
        supabase
        .table("goals")
        .select("*")
        .order("target_date")
        .execute()
    )

    goals = goals_response.data


    return render_template(
        "dashboard.html",
        tasks=tasks,
        events=events,
        goals=goals
    )


# ==============================
# ADD TASK
# ==============================

@app.route(
    "/add-task",
    methods=["GET", "POST"]
)
def add_task():

    if request.method == "POST":

        title = request.form["title"]

        description = request.form.get(
            "description",
            ""
        )

        task_date = request.form["task_date"]

        task_hour = int(
            request.form["task_hour"]
        )

        task_minute = int(
            request.form["task_minute"]
        )

        task_period = request.form[
            "task_period"
        ]


        # Convert AM/PM to 24-hour format

        if task_period == "AM":

            if task_hour == 12:
                task_hour = 0

        else:

            if task_hour != 12:
                task_hour += 12


        task_time = (
            f"{task_hour:02d}:"
            f"{task_minute:02d}:00"
        )


        repeat_type = request.form[
            "repeat_type"
        ]


        reminder_enabled = (
            "reminder_enabled"
            in request.form
        )


        music_enabled = (
            "music_enabled"
            in request.form
        )


        # Insert task

        supabase.table("tasks").insert({

            "title": title,

            "description": description,

            "task_date": task_date,

            "task_time": task_time,

            "repeat_type": repeat_type,

            "reminder_enabled":
                reminder_enabled,

            "music_enabled":
                music_enabled,

            "status": "pending"

        }).execute()


        return redirect("/")


    return render_template(
        "add_task.html"
    )


# ==============================
# ADD EVENT
# ==============================

@app.route(
    "/add-event",
    methods=["GET", "POST"]
)
def add_event():

    if request.method == "POST":

        title = request.form["title"]

        description = request.form.get(
            "description",
            ""
        )

        event_date = request.form[
            "event_date"
        ]

        event_hour = int(
            request.form["event_hour"]
        )

        event_minute = int(
            request.form["event_minute"]
        )

        event_period = request.form[
            "event_period"
        ]


        # Convert AM/PM

        if event_period == "AM":

            if event_hour == 12:
                event_hour = 0

        else:

            if event_hour != 12:
                event_hour += 12


        event_time = (
            f"{event_hour:02d}:"
            f"{event_minute:02d}:00"
        )


        # ==========================
        # REMINDER SETTINGS
        # ==========================

        reminder_enabled = (
            "reminder_enabled"
            in request.form
        )


        reminder_type = request.form.get(
            "reminder_type",
            "minutes"
        )


        reminder_before_minutes = int(
            request.form.get(
                "reminder_before_minutes",
                30
            )
        )


        reminder_before_days = int(
            request.form.get(
                "reminder_before_days",
                0
            )
        )


        # Minutes selected

        if reminder_type == "minutes":

            reminder_before_days = 0


        # Days selected

        elif reminder_type == "days":

            reminder_before_minutes = 0


        # ==========================
        # INSERT EVENT
        # ==========================

        supabase.table("events").insert({

            "title": title,

            "description": description,

            "event_date": event_date,

            "event_time": event_time,

            "reminder_enabled":
                reminder_enabled,

            "reminder_before_minutes":
                reminder_before_minutes,

            "reminder_before_days":
                reminder_before_days,

            "status": "upcoming"

        }).execute()


        return redirect("/")


    return render_template(
        "add_event.html"
    )


# ==============================
# EDIT TASK
# ==============================

@app.route(
    "/edit-task/<int:task_id>",
    methods=["GET", "POST"]
)
def edit_task(task_id):

    response = (
        supabase
        .table("tasks")
        .select("*")
        .eq("id", task_id)
        .single()
        .execute()
    )

    task = response.data


    if not task:
        return redirect("/")


    # ==========================
    # SAVE EDITED TASK
    # ==========================

    if request.method == "POST":

        title = request.form["title"]

        description = request.form.get(
            "description",
            ""
        )

        task_date = request.form[
            "task_date"
        ]

        task_hour = int(
            request.form["task_hour"]
        )

        task_minute = int(
            request.form["task_minute"]
        )

        task_period = request.form[
            "task_period"
        ]


        # Convert AM/PM

        if task_period == "AM":

            if task_hour == 12:
                task_hour = 0

        else:

            if task_hour != 12:
                task_hour += 12


        task_time = (
            f"{task_hour:02d}:"
            f"{task_minute:02d}:00"
        )


        repeat_type = request.form[
            "repeat_type"
        ]


        reminder_enabled = (
            "reminder_enabled"
            in request.form
        )


        music_enabled = (
            "music_enabled"
            in request.form
        )


        # Update task

        supabase.table("tasks").update({

            "title": title,

            "description": description,

            "task_date": task_date,

            "task_time": task_time,

            "repeat_type": repeat_type,

            "reminder_enabled":
                reminder_enabled,

            "music_enabled":
                music_enabled,

            "status": "pending"

        }).eq(
            "id",
            task_id
        ).execute()


        return redirect("/")


    # ==========================
    # PREPARE TIME
    # ==========================

    database_time = task[
        "task_time"
    ]

    hour_24 = int(
        database_time[:2]
    )

    minute = database_time[3:5]


    if hour_24 == 0:

        hour_12 = 12
        period = "AM"

    elif hour_24 < 12:

        hour_12 = hour_24
        period = "AM"

    elif hour_24 == 12:

        hour_12 = 12
        period = "PM"

    else:

        hour_12 = hour_24 - 12
        period = "PM"


    return render_template(
        "edit_task.html",
        task=task,
        hour=hour_12,
        minute=minute,
        period=period
    )


# ==============================
# EDIT EVENT
# ==============================

@app.route(
    "/edit-event/<int:event_id>",
    methods=["GET", "POST"]
)
def edit_event(event_id):

    response = (
        supabase
        .table("events")
        .select("*")
        .eq("id", event_id)
        .single()
        .execute()
    )

    event = response.data


    if not event:
        return redirect("/")


    # ==========================
    # SAVE EDITED EVENT
    # ==========================

    if request.method == "POST":

        title = request.form["title"]

        description = request.form.get(
            "description",
            ""
        )

        event_date = request.form[
            "event_date"
        ]

        event_hour = int(
            request.form["event_hour"]
        )

        event_minute = int(
            request.form["event_minute"]
        )

        event_period = request.form[
            "event_period"
        ]


        # Convert AM/PM

        if event_period == "AM":

            if event_hour == 12:
                event_hour = 0

        else:

            if event_hour != 12:
                event_hour += 12


        event_time = (
            f"{event_hour:02d}:"
            f"{event_minute:02d}:00"
        )


        # ==========================
        # REMINDER SETTINGS
        # ==========================

        reminder_enabled = (
            "reminder_enabled"
            in request.form
        )


        reminder_type = request.form.get(
            "reminder_type",
            "minutes"
        )


        reminder_before_minutes = int(
            request.form.get(
                "reminder_before_minutes",
                30
            )
        )


        reminder_before_days = int(
            request.form.get(
                "reminder_before_days",
                0
            )
        )


        if reminder_type == "minutes":

            reminder_before_days = 0

        elif reminder_type == "days":

            reminder_before_minutes = 0


        # ==========================
        # UPDATE EVENT
        # ==========================

        supabase.table("events").update({

            "title": title,

            "description": description,

            "event_date": event_date,

            "event_time": event_time,

            "reminder_enabled":
                reminder_enabled,

            "reminder_before_minutes":
                reminder_before_minutes,

            "reminder_before_days":
                reminder_before_days,

            "status": "upcoming"

        }).eq(
            "id",
            event_id
        ).execute()


        return redirect("/")


    # ==========================
    # PREPARE TIME
    # ==========================

    database_time = event[
        "event_time"
    ]

    hour_24 = int(
        database_time[:2]
    )

    minute = database_time[3:5]


    if hour_24 == 0:

        hour_12 = 12
        period = "AM"

    elif hour_24 < 12:

        hour_12 = hour_24
        period = "AM"

    elif hour_24 == 12:

        hour_12 = 12
        period = "PM"

    else:

        hour_12 = hour_24 - 12
        period = "PM"


    return render_template(
        "edit_event.html",
        event=event,
        hour=hour_12,
        minute=minute,
        period=period
    )


# ==============================
# ADD GOAL
# ==============================

@app.route(
    "/add-goal",
    methods=["POST"]
)
def add_goal():

    title = request.form.get(
        "title",
        ""
    ).strip()


    description = request.form.get(
        "description",
        ""
    ).strip()


    target_date = request.form.get(
        "target_date",
        ""
    )


    if title:

        supabase.table("goals").insert({

            "title": title,

            "description": description,

            "target_date":
                target_date
                if target_date
                else None,

            "status": "pending"

        }).execute()


    return redirect("/")


# ==============================
# COMPLETE GOAL
# ==============================

@app.route(
    "/complete-goal/<int:goal_id>",
    methods=["POST"]
)
def complete_goal(goal_id):

    supabase.table("goals").update({

        "status": "completed"

    }).eq(
        "id",
        goal_id
    ).execute()


    return redirect("/")


# ==============================
# DELETE GOAL
# ==============================

@app.route(
    "/delete-goal/<int:goal_id>",
    methods=["POST"]
)
def delete_goal(goal_id):

    supabase.table("goals") \
        .delete() \
        .eq(
            "id",
            goal_id
        ) \
        .execute()


    return redirect("/")


# ==============================
# DELETE TASK
# ==============================

@app.route(
    "/delete-task/<int:task_id>",
    methods=["POST"]
)
def delete_task(task_id):

    supabase.table("tasks") \
        .delete() \
        .eq(
            "id",
            task_id
        ) \
        .execute()


    return redirect("/")


# ==============================
# DELETE EVENT
# ==============================

@app.route(
    "/delete-event/<int:event_id>",
    methods=["POST"]
)
def delete_event(event_id):

    supabase.table("events") \
        .delete() \
        .eq(
            "id",
            event_id
        ) \
        .execute()


    return redirect("/")


# ==============================
# REMINDER STATUS
# ==============================

@app.route("/reminder-status")
def reminder_status():

    return {
        "reminder":
            reminder.latest_reminder
    }


# ==============================
# START APPLICATION
# ==============================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )